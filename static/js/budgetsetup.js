// Function to update the table with the new item
    function addRowToTable(item, tableId, dataRow) {
        rowCountE++;

        // Remove "No data" row if it exists
        const noDataRow = document.querySelector(dataRow);
        if (noDataRow) {
            noDataRow.remove();
        }

        // Add the new item to the table
        const tableBody = document.querySelector(tableId);
        const newRow = document.createElement('tr');

        const rowIndexCell = document.createElement('td');
        rowIndexCell.textContent = rowCountE;

        const nameCell = document.createElement('td');
        nameCell.textContent = item.name;

        const amountCell = document.createElement('td');
        amountCell.textContent = item.amount;

        const descriptionCell = document.createElement('td');
        descriptionCell.textContent = item.description;

        newRow.appendChild(rowIndexCell);
        newRow.appendChild(nameCell);
        newRow.appendChild(amountCell);
        newRow.appendChild(descriptionCell);

        tableBody.appendChild(newRow);
    }

    // Function to clear input fields
    function clearInputFields(inputs) {
        inputs.forEach(input => input.value = '');
    }

    // Function to close the modal
    function closeModal(modalId) {
        const modal = bootstrap.Modal.getInstance(document.querySelector(modalId));
        modal.hide();
    }


    let rowCountI = 0;  // Keep track of the number of rows
    let totalIncomeValue = 0;  // Keep track of the total income

    // JavaScript to handle form submission
    async function addItem(event) {
        event.preventDefault();  // Prevent the default form submission

        // Get values from the input fields
        const incomeNameInput = document.querySelector('#incomeNameInput');
        const incomeInput = document.querySelector('#incomeInput');
        const budgetIdInput = document.querySelector('#budgetIdInput')
        const dateInput = document.querySelector('#dateInput')
        const descriptionInput = document.querySelector('#descriptionInput');

        const incomeName = incomeNameInput.value.trim();
        const income = parseFloat(incomeInput.value.trim());
        const budget_id = budgetIdInput.value.trim();
        const dateIn = dateInput.value.trim();
        const description = descriptionInput.value.trim();

        if (!incomeName || !income || !budget_id || !description) return;  // Don't submit if any field is empty

        try {
            // Send the data to the server using Fetch API
            const response = await fetch('/add_income', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: incomeName,
                    amount: income,
                    description: description,
                    date: dateIn,
                    budget_id: budget_id,
                })
            });

            const data = await response.json();
            console.log(data)

            if (data.success) {
                rowCountI++;

                // Remove "No data" row if it exists
                addRowToTable(data.item, '#itemTableBody', '#noDataRow')


                // Update the total income
                totalIncomeValue += data.item.amount;
                document.querySelector('#totalIncome').textContent = totalIncomeValue.toFixed(2);

                // Clear the input fields
                clearInputFields([incomeNameInput, incomeInput, descriptionInput.value])

                // Close the modal
                closeModal('#exampleModal')

            } else {
                alert('Error adding item');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }


    let rowCountE = 0;  // Keep track of the number of rows
    let totalExpenseValue = 0;  // Keep track of the total income



    // Async function to handle form submission for expenses
    async function addRecurringExpense(event) {
        event.preventDefault();  // Prevent the default form submission

        // Get values from the input fields
        const expenseNameInput = document.querySelector('#expenseNameInput');
        const expenseInput = document.querySelector('#expenseInput');
        const budget_id = document.querySelector('#budgetId2Input')
        const category2Input = document.querySelector('#category2Input')
        const date2Input = document.querySelector('#date2Input')
        const descriptionInput = document.querySelector('#description2Input');

        const expenseName = expenseNameInput.value.trim();
        const expense = parseFloat(expenseInput.value.trim());
        const budget_id2 = budget_id.value;
        const category = category2Input.value;
        const date = date2Input.value;
        const description = descriptionInput.value.trim();
        console.log(budget_id2)
        // Basic validation for empty fields
        if (!expenseName || isNaN(expense) || !description) {
            alert("Please fill in all fields correctly.");
            return;
        }

        try {
            // Send the data to the server using Fetch API
            const response = await fetch('/create_transaction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    amount: expense,
                    name: expenseName,
                    category: category,
                    date: date,
                    budget_id: budget_id2,
                    description: description,
                    recurring: true, // check a check box to determain if true or not
                })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            if (data.success) {
                // Update the table with the new item
                addRowToTable(data.item, '#itemTable2body', '#noData2Row');

                // Update the total expense
                totalExpenseValue += data.item.amount;
                document.querySelector('#totalExpense').textContent = totalExpenseValue.toFixed(2);

                // Clear the input fields
                clearInputFields([incomeNameInput, incomeInput, descriptionInput]);

                // Close the modal
                closeModal('#expenseModal');
            } else {
                alert('Error adding item');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    }

document.addEventListener('DOMContentLoaded', function () {
    const expenses = JSON.parse(document.getElementById('expensesData').textContent);
    const incomes = JSON.parse(document.getElementById('incomesData').textContent);

    const tableExpenseBody = document.getElementById('itemTable2Body');
    const tableIncomeBody = document.getElementById('itemTableBody');
    tableExpenseBody.innerHTML = '';
    tableIncomeBody.innerHTML = '';
    if (incomes.length === 0) {
    tableIncomeBody.innerHTML = `
        <tr id="noDataRow">
            <td colspan="4" class="text-center">No data available</td>
        </tr>`;
} else {
    incomes.forEach(income => {
        rowCountI ++;
        const row = `
            <tr>
                <td id="rowIndexICell">${rowCountI}</td>
                <td id="nameICell">${income.name}</td>
                <td id="amountICell">${income.amount}</td>
                <td id="descriptionICell">${income.description}</td>
            </tr>`;
        tableIncomeBody.innerHTML += row;
    });
    }

    if (expenses.length === 0) {
        tableExpenseBody.innerHTML = `
            <tr id="noData2Row">
                <td colspan="4" class="text-center">No data available</td>
            </tr>`;
    } else {
        expenses.forEach(expense => {
            rowCountE ++;
            const row = `
                <tr>
                    <td id="rowIndexECell">${rowCountE}</td>
                    <td id="nameECell">${expense.name}</td>
                    <td id="amountECell">${expense.amount}</td>
                    <td id="descriptionECell">${expense.description}</td>
                </tr>`;
            tableExpenseBody.innerHTML += row;
        });
    }
});
