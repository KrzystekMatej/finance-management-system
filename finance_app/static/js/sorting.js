function sortTransactions(sortType, clickedIcon, month, year, source) {
  
  // source indicates whether it was called from main page or from statistics modal
  const id = "sort-control-" + month + "-" + year + "-" + source;
  const sortControl = document.getElementById(id);

  const allIcons = sortControl.querySelectorAll('i');
  allIcons.forEach(icon => {
      icon.classList.add('opacity-half');
      icon.classList.remove('opacity-full');
  });

  clickedIcon.classList.remove('opacity-half');
  clickedIcon.classList.add('opacity-full');

  const summaryBody = sortControl.closest('.summary-module').querySelector('.summary-body');
  const transactions = Array.from(summaryBody.querySelectorAll(".transaction"));

  // Sort by transaction date
  if (sortType == "date-asc" || sortType == "date-desc") {
      const transactionsWithDates = transactions.map(transaction => {
          const dateString = transaction.querySelector(".transaction-date").innerHTML;
          const dateValue = parseDateString(dateString);
          return {
              transaction,
              dateValue
          };
      });

      if (sortType == "date-asc") {
          transactionsWithDates.sort((a, b) => a.dateValue - b.dateValue);
      } else {
          transactionsWithDates.sort((a, b) => b.dateValue - a.dateValue);
      }

      transactionsWithDates.forEach(item => {
          summaryBody.appendChild(item.transaction);
      });
  }

  // Sort by transaction name
  if (sortType == "name-asc" || sortType == "name-desc") {
      const transactionsWithNames = transactions.map(transaction => {
          const name = transaction.querySelector(".transaction-name").innerHTML.trim().toLowerCase();
          return {
              transaction,
              name
          };
      });

      if (sortType == "name-asc") {
          transactionsWithNames.sort((a, b) => a.name.localeCompare(b.name));
      } else {
          transactionsWithNames.sort((a, b) => b.name.localeCompare(a.name));
      }

      transactionsWithNames.forEach(item => {
          summaryBody.appendChild(item.transaction);
      });
  }

  // Sort by category
  if (sortType == "category-asc" || sortType == "category-desc") {
      const transactionsWithCategories = transactions.map(transaction => {
          const categoryName = transaction.querySelector(".transaction-category").innerHTML.trim().toLowerCase();
          return {
              transaction,
              categoryName
          };
      });

      if (sortType == "category-asc") {
          transactionsWithCategories.sort((a, b) => a.categoryName.localeCompare(b.categoryName));
      } else {
          transactionsWithCategories.sort((a, b) => b.categoryName.localeCompare(a.categoryName));
      }

      transactionsWithCategories.forEach(item => {
          summaryBody.appendChild(item.transaction);
      });
  }

  // Sort by transaction amount
  if (sortType == "amount-asc" || sortType == "amount-desc") {
      const transactionsWithAmounts = transactions.map(transaction => {
          const amountString = transaction.querySelector(".transaction-amount").innerHTML.trim();
          const amount = parseAmount(amountString);
          return {
              transaction,
              amount
          };
      });

      if (sortType == "amount-asc") {
          transactionsWithAmounts.sort((a, b) => a.amount - b.amount);
      } else {
          transactionsWithAmounts.sort((a, b) => b.amount - a.amount);
      }

      transactionsWithAmounts.forEach(item => {
          summaryBody.appendChild(item.transaction);
      });
  }
}

// Function to parse the amount string ('+123 456 Kč' etc) into a number
function parseAmount(amountStr) {
  const amount = amountStr.replace(/[^\d.-]/g, ''); // Keep only digits and minus/period
  return parseFloat(amount);
}

function parseDateString(dateStr) {
  const monthMap = {
      0: ['leden', 'ledna'],
      1: ['únor', 'února'],
      2: ['březen', 'března'],
      3: ['duben', 'dubna'],
      4: ['květen', 'května'],
      5: ['červen', 'června'],
      6: ['červenec', 'července'],
      7: ['srpen', 'srpna'],
      8: ['září'],
      9: ['říjen', 'října'],
      10: ['listopad', 'listopadu'],
      11: ['prosinec', 'prosince']
  };

  const [day, monthName, year, time] = dateStr.split(' ');
  let month = -1;

  // find the matching month name
  for (let [monthNumber, variations] of Object.entries(monthMap)) {
      if (variations.includes(monthName.toLowerCase())) {
          month = parseInt(monthNumber);
          break;
      }
  }

  const [hours, minutes] = time.split(':'); 
  return new Date(year, month, day, hours, minutes);
}