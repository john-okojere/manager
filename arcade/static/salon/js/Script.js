let totalAmount = 0;
let quantity = 1; // Default quantity
let activeField = "quantityInput"; // Default active field
let saleId = null; // Global variable to track the current sale ID

function addItem(itemName, itemPrice, itemID) {
    const price = itemPrice; // Example fixed price per item
    const tbody = document.getElementById('transactionBody');
    const row = document.createElement('tr');
    const itemTotal = quantity * price;
    row.innerHTML = `<td>${itemID}</td><td>${quantity}</td><td>${itemName}</td><td> ₦${price.toFixed(2)}</td><td> ₦${itemTotal.toFixed(2)}</td>`;
    tbody.appendChild(row);
    totalAmount += itemTotal;
    document.getElementById('total').innerText = totalAmount.toFixed(2);

    // If this is the first item, create the sale
    if (!saleId) {
        const cashierId = document.getElementById('cashierId').value; // Hidden input for cashier ID

        $.ajax({
            url: '/salon/create-sale/',
            method: 'POST',
            data: {
                cashier_id: cashierId,
                total_amount: totalAmount,
                csrfmiddlewaretoken: document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            success: function(response) {
                saleId = response.sale_id; // Save the sale ID for subsequent items
                addSaleItem(itemID, itemName, price, quantity); // Add the first item after creating the sale
            },
            error: function() {
                alert('Failed to create sale.');
            }
        });
    } else {
        // Add the item to the existing sale
        addSaleItem(itemID, itemName, price, quantity);
    }

    // Reset quantity to 1 after adding an item
    quantity = 1;
    document.getElementById('quantityInput').value = '';
}

function addSaleItem(itemID, itemName, price, quantity) {
    $.ajax({
        url: '/salon/add-sale-item/',
        method: 'POST',
        data: {
            sale_id: saleId,
            product_id: itemID,
            quantity: quantity,
            price: price,
            csrfmiddlewaretoken: document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        success: function(response) {
            console.log(`Item added to sale: ${itemName} x${quantity}`);
        },
        error: function() {
            alert(`Failed to add item: ${itemName}`);
        }
    });
}


// Append number to the active field
function appendNumber(num) {
    const input = document.getElementById(activeField);
    input.value += num;

    if (activeField === "quantityInput") {
        quantity = parseInt(input.value) || 1;
    }
}

// Clear the active field
function clearInput() {
    const input = document.getElementById(activeField);
    input.value = '';

    if (activeField === "quantityInput") {
        quantity = 1;
    }
}

// Remove the last digit from the active field
function backspace() {
    const input = document.getElementById(activeField);
    input.value = input.value.slice(0, -1);

    if (activeField === "quantityInput") {
        quantity = parseInt(input.value) || 1;
    }
}

// Update payment details as user types in the amount input field
function updatePayment() {
    const paidAmount = parseFloat(document.getElementById('amountInput').value) || 0;
    document.getElementById('amountPaid').innerText = paidAmount.toFixed(2);
    const due = Math.max(totalAmount - paidAmount, 0);
    document.getElementById('amountDue').innerText = due.toFixed(2);
}

// Set the active field to the quantity input
function focusQuantityInput() {
    activeField = "quantityInput";
}

// Set the active field to the amount input
function focusAmountInput() {
    activeField = "amountInput";
}


// Specify the payment method
function pay(method) {
    const paidAmount = parseFloat(document.getElementById('amountInput').value) || 0; // Get the paid amount
    const due = paidAmount - totalAmount; // Calculate the difference

    const amountDueElement = document.getElementById('amountDue');
    const amountPaidElement = document.getElementById('amountPaid');

    // Update the amount paid and due
    amountPaidElement.innerText = paidAmount.toFixed(2);
    amountDueElement.innerText = due.toFixed(2);

    // Update colors
    if (due < 0) {
        amountDueElement.style.color = "red"; // Customer owes you
        alert(`The customer still owes $${Math.abs(due).toFixed(2)}.`);
    } else if (due > 0) {
        amountDueElement.style.color = "green"; // You owe the customer change
        alert(`You owe the customer $${due.toFixed(2)} in change.`);
    } else {
        amountDueElement.style.color = "black"; // Exact payment
        alert(`Payment is exact. Thank you for paying via ${method}!`);
    }

    if (due >= 0) {
        // If the payment is complete or more, print the receipt and clear the transaction
        printReceipt(paidAmount, due, method);
        clearTransaction();
    }
}

// Function to print a receipt
function printReceipt(paidAmount, change, method) {
    const tbody = document.getElementById('transactionBody');
    const rows = tbody.getElementsByTagName('tr');
    const receiptData = [];

    // Collect transaction details
    for (let i = 0; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        receiptData.push({
            quantity: cells[0].innerText,
            description: cells[1].innerText,
            price: cells[2].innerText,
            total: cells[3].innerText,
        });
    }

    // Generate receipt content
    let receiptContent = `
        <div style="text-align: center; font-family: Arial, sans-serif; margin: 20px;">
            <h2>Elegante Arcade</h2>
            <p>No 1 Bria Street Ademola Adetokunbo Crescent<br>Wuse 2 Abuja</p>
            <p>07068686839</p>
            <p>${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}</p>
            <p>CHECK# 100022</p>
            <hr>
            <table style="width: 100%; text-align: left; margin-bottom: 20px;">
                <thead>
                    <tr>
                        <th>QTY</th>
                        <th>Description</th>
                        <th>Price</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
    `;

    // Add transaction rows to receipt
    receiptData.forEach((item) => {
        receiptContent += `
            <tr>
                <td>${item.quantity}</td>
                <td>${item.description}</td>
                <td>${item.price}</td>
                <td>${item.total}</td>
            </tr>
        `;
    });

    // Add total, VAT, and payment info
    receiptContent += `
                </tbody>
            </table>
            <hr>
            <p><strong>TOTAL NGN: ${totalAmount.toFixed(2)}</strong></p>
            <p>VAT 7.5%</p>
            <p>Cashier# 1</p>
            <p>You have been served by User</p>
            <p><strong>Paid: NGN ${paidAmount.toFixed(2)}</strong></p>
            <p><strong>Change: NGN ${change.toFixed(2)}</strong></p>
            <hr>
            <p>Powered by digi02.org</p>
        </div>
    `;

    // Display the receipt in a new window for printing
    const receiptWindow = window.open("", "Receipt", "width=400,height=600");
    receiptWindow.document.write(receiptContent);
    receiptWindow.document.close();
    receiptWindow.print();
}

// Function to clear the transaction
function clearTransaction() {
    document.getElementById('transactionBody').innerHTML = ''; // Clear table rows
    totalAmount = 0;
    document.getElementById('total').innerText = totalAmount.toFixed(2);
    document.getElementById('amountPaid').innerText = '0.00';
    document.getElementById('amountDue').innerText = '0.00';
    document.getElementById('amountInput').value = '';
    document.getElementById('amountDue').style.color = "black"; // Reset color
}


// Refund placeholder
function refund() {
    alert('Refund feature is not implemented yet.');
}
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}
// Clear all transactions
function clearTransaction() {
   saleId = null
    document.getElementById('transactionBody').innerHTML = '';
    totalAmount = 0;
    document.getElementById('total').innerText = totalAmount.toFixed(2);
    document.getElementById('amountPaid').innerText = '0.00';
    document.getElementById('amountDue').innerText = '0.00';
    document.getElementById('amountInput').value = '';
}


// Open the discount overlay
function openDiscountOverlay() {
    document.getElementById('discountOverlay').style.display = 'flex';
}

// Close the discount overlay
function closeDiscountOverlay() {
    document.getElementById('discountOverlay').style.display = 'none';
    document.getElementById('discountPercentage').value = '';
    document.getElementById('discountType').value = 'total';
    document.getElementById('itemIndex').style.display = 'none';
    document.getElementById('itemIndexLabel').style.display = 'none';
}

// Show the item index input when "Specific Item" is selected
document.getElementById('discountType').addEventListener('change', function () {
    const itemIndexInput = document.getElementById('itemIndex');
    const itemIndexLabel = document.getElementById('itemIndexLabel');
    if (this.value === 'item') {
        itemIndexInput.style.display = 'block';
        itemIndexLabel.style.display = 'block';
    } else {
        itemIndexInput.style.display = 'none';
        itemIndexLabel.style.display = 'none';
    }
});

function applyDiscount() {
    const discountPercentage = parseFloat(document.getElementById('discountPercentage').value) || 0;
    const discountType = document.getElementById('discountType').value;

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    if (discountType === 'total') {
        // Apply discount to the total
        const discountAmount = (totalAmount * discountPercentage) / 100;
        totalAmount -= discountAmount;
        document.getElementById('total').innerText = totalAmount.toFixed(2);
        console.log('asssa')
        // Send AJAX request to create SaleDiscount
        $.ajax({
            url: '/salon/apply-sale-discount/',
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken },
            data: {
                cashier_id: 1,  // Replace with actual cashier ID
                sale_id: 1,     // Replace with actual sale ID
                proposed_discount: discountAmount
            },
            success: function (response) {
                alert(response.message);
            },
            error: function () {
                alert('Failed to apply discount.');
            }
        });

    } else if (discountType === 'item') {
        // Apply discount to a specific item
        const itemIndex = parseInt(document.getElementById('itemIndex').value) - 1; // Convert 1-based index to 0-based
        const tbody = document.getElementById('transactionBody');
        const rows = tbody.getElementsByTagName('tr');

        if (itemIndex >= 0 && itemIndex < rows.length) {
            const cells = rows[itemIndex].getElementsByTagName('td');
            const itemTotal = parseFloat(cells[3].innerText.replace('₦', ''));
            const discountAmount = (itemTotal * discountPercentage) / 100;
            const newTotal = itemTotal - discountAmount;
            cells[3].innerText = `₦${newTotal.toFixed(2)}`;

            // Update the grand total
            totalAmount -= discountAmount;
            document.getElementById('total').innerText = totalAmount.toFixed(2);

            // Send AJAX request to create SaleItemDiscount
            $.ajax({
                url: '/salon/apply-sale-item-discount/',
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken },
                data: {
                    cashier_id: 1,       // Replace with actual cashier ID
                    sale_item_id: 1,    // Replace with actual sale item ID
                    proposed_discount: discountAmount
                },
                success: function (response) {
                    alert(response.message);
                },
                error: function () {
                    alert('Failed to apply item discount.');
                }
            });

        } else {
            alert('Invalid item index.');
        }
    }

    closeDiscountOverlay();
}

// Open the refund overlay
function openRefundOverlay() {
    document.getElementById('refundOverlay').style.display = 'flex';
}

// Close the refund overlay
function closeRefundOverlay() {
    document.getElementById('refundOverlay').style.display = 'none';
    document.getElementById('refundReason').value = 'Changed their mind'; // Reset dropdown
    document.getElementById('additionalReason').style.display = 'none';
    document.getElementById('additionalReasonLabel').style.display = 'none';
    document.getElementById('additionalReason').value = ''; // Clear text area
}

// Handle changes in the refund reason dropdown
function handleRefundReasonChange() {
    const refundReason = document.getElementById('refundReason').value;
    const additionalReasonField = document.getElementById('additionalReason');
    const additionalReasonLabel = document.getElementById('additionalReasonLabel');

    if (refundReason === 'Other') {
        additionalReasonField.style.display = 'block';
        additionalReasonLabel.style.display = 'block';
    } else {
        additionalReasonField.style.display = 'none';
        additionalReasonLabel.style.display = 'none';
    }
}

// Process the refund
function processRefund() {
    const refundReason = document.getElementById('refundReason').value;
    const additionalReason = document.getElementById('additionalReason').value;

    // Combine the refund reason and additional reason
    let fullReason = refundReason;
    if (refundReason === 'Other' && additionalReason) {
        fullReason = `Other: ${additionalReason}`;
    }

    // Show a confirmation (you could integrate this with a backend for tracking)
    alert(`Refund processed.\nReason: ${fullReason}`);

    // Clear transaction data
    clearTransaction();

    // Close the overlay
    closeRefundOverlay();
}
// Function to open the menu overlay
function openMenu() {
    document.getElementById('menuOverlay').style.display = 'flex';
}

// Function to close the menu overlay
function closeMenu() {
    document.getElementById('menuOverlay').style.display = 'none';
}

// Placeholder functions for menu buttons
function previewOlderSales() {
    alert("Preview Older Sales feature coming soon!");
}

function printLastReceipt() {
    alert("Print Last Receipt feature coming soon!");
}

function applyDiscount() {
    alert("Discount feature coming soon!");
}

function setPrice() {
    alert("Set Price feature coming soon!");
}

function viewSalesHistory() {
    alert("Sales History feature coming soon!");
}

function logout() {
    alert("Log Out feature coming soon!");
}

function endOfDay() {
    alert("End of Day feature coming soon!");
}

function goBack() {
    closeMenu();
}
// Open the discount overlay
function openDiscountOverlay() {
    document.getElementById('discountOverlay').style.display = 'flex';
}

// Close the discount overlay
function closeDiscountOverlay() {
    document.getElementById('discountOverlay').style.display = 'none';
    document.getElementById('discountPercentage').value = '';
    document.getElementById('itemIndex').value = '';
    document.getElementById('itemIndex').style.display = 'none';
    document.getElementById('itemIndexLabel').style.display = 'none';
}

// Toggle item index input for specific item discounts
function toggleItemIndexInput() {
    const discountType = document.getElementById('discountType').value;
    const itemIndexField = document.getElementById('itemIndex');
    const itemIndexLabel = document.getElementById('itemIndexLabel');

    if (discountType === 'item') {
        itemIndexField.style.display = 'block';
        itemIndexLabel.style.display = 'block';
    } else {
        itemIndexField.style.display = 'none';
        itemIndexLabel.style.display = 'none';
    }
}

// Apply discount
function applyDiscount() {
    const discountPercentage = parseFloat(document.getElementById('discountPercentage').value) || 0;
    const discountType = document.getElementById('discountType').value;

    if (discountType === 'total') {
        // Apply discount to the total
        const discountAmount = (totalAmount * discountPercentage) / 100;
        totalAmount -= discountAmount;
        document.getElementById('total').innerText = totalAmount.toFixed(2);

        // AJAX call to create SaleDiscount
       
        const cashierId = document.getElementById('cashierId').value; // Hidden input for cashier ID

        $.ajax({
            url: '/salon/create-sale-discount/',
            method: 'POST',
            data: {
                sale_id: saleId,
                proposed_discount: discountAmount,
                csrfmiddlewaretoken: document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            success: function(response) {
                alert(response.message);
            },
            error: function() {
                alert('Failed to create sale discount.');
            }
        });

        alert(`Discount of ${discountPercentage}% applied to total. New Total: ₦${totalAmount.toFixed(2)}`);
    } else if (discountType === 'item') {
        // Apply discount to a specific item
        const itemIndex = parseInt(document.getElementById('itemIndex').value) - 1;
        const tbody = document.getElementById('transactionBody');
        const rows = tbody.getElementsByTagName('tr');

        if (itemIndex >= 0 && itemIndex < rows.length) {
            const cells = rows[itemIndex].getElementsByTagName('td');
            const itemTotal = parseFloat(cells[3].innerText.replace('₦', ''));
            const discountAmount = (itemTotal * discountPercentage) / 100;
            const newTotal = itemTotal - discountAmount;
            cells[3].innerText = `₦${newTotal.toFixed(2)}`;

            // Update the grand total
            totalAmount -= discountAmount;
            document.getElementById('total').innerText = totalAmount.toFixed(2);

            // AJAX call to create SaleItemDiscount
            const saleItemId = rows[itemIndex].dataset.saleItemId; // Assume each row has a data attribute for sale item ID
            const cashierId = document.getElementById('cashierId').value; // Hidden input for cashier ID

            $.ajax({
                url: '/salon/create-sale-item-discount/',
                method: 'POST',
                data: {
                    sale_item_id: saleItemId,
                    proposed_discount: discountAmount,
                    csrfmiddlewaretoken: document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                success: function(response) {
                    alert(response.message);
                },
                error: function() {
                    alert('Failed to create sale item discount.');
                }
            });

            alert(`Discount of ${discountPercentage}% applied to item. New Item Total: ₦${newTotal.toFixed(2)}`);
        } else {
            alert('Invalid item index.');
        }
    }

    closeDiscountOverlay();
}

let heldTransactions = []; // Array to store held transactions

// Hold the current transaction
function holdTransaction() {
    const tbody = document.getElementById("transactionBody");
    const rows = tbody.getElementsByTagName("tr");
    const currentTransaction = [];

    // Store each row in the held transaction
    for (let row of rows) {
        const cells = row.getElementsByTagName("td");
        currentTransaction.push({
            quantity: cells[0].innerText,
            description: cells[1].innerText,
            price: cells[2].innerText,
            total: cells[3].innerText,
        });
    }

    heldTransactions.push(currentTransaction); // Save the current transaction
    alert("Transaction held successfully!");
    clearTransaction(); // Clear the current transaction
}

// Recall a held transaction
function recallTransaction() {
    if (heldTransactions.length === 0) {
        alert("No held transactions to recall.");
        return;
    }

    const recalledTransaction = heldTransactions.pop(); // Get the most recent held transaction
    const tbody = document.getElementById("transactionBody");

    for (let item of recalledTransaction) {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${item.quantity}</td>
            <td>${item.description}</td>
            <td>${item.price}</td>
            <td>${item.total}</td>
        `;
        tbody.appendChild(row);
    }

    alert("Transaction recalled successfully!");
}
// Set custom price for the last added item
function setPrice() {
    const price = parseFloat(prompt("Enter the new price for the last item:")) || 0;

    if (price <= 0) {
        alert("Invalid price.");
        return;
    }

    const tbody = document.getElementById("transactionBody");
    const rows = tbody.getElementsByTagName("tr");

    if (rows.length === 0) {
        alert("No items to update.");
        return;
    }

    const lastRow = rows[rows.length - 1]; // Get the last row
    const quantity = parseInt(lastRow.cells[0].innerText);
    const newTotal = quantity * price;

    lastRow.cells[2].innerText = `$${price.toFixed(2)}`; // Update the price cell
    lastRow.cells[3].innerText = `$${newTotal.toFixed(2)}`; // Update the total cell

    // Update the overall total
    const oldTotal = parseFloat(lastRow.cells[3].innerText.replace("$", ""));
    totalAmount += newTotal - oldTotal;
    document.getElementById("total").innerText = totalAmount.toFixed(2);

    alert("Price updated successfully.");
}
let salesHistory = []; // Array to store completed sales

// Save the current sale to the history
function saveSale(paidAmount, method) {
    const tbody = document.getElementById("transactionBody");
    const rows = tbody.getElementsByTagName("tr");
    const transaction = [];

    for (let row of rows) {
        const cells = row.getElementsByTagName("td");
        transaction.push({
            quantity: cells[0].innerText,
            description: cells[1].innerText,
            price: cells[2].innerText,
            total: cells[3].innerText,
        });
    }

    salesHistory.push({
        date: new Date(),
        items: transaction,
        total: totalAmount.toFixed(2),
        paid: paidAmount.toFixed(2),
        method: method,
    });

    alert("Sale saved to history.");
}

// View sales history
function viewSalesHistory() {
    const historyOverlay = document.createElement("div");
    historyOverlay.style.position = "fixed";
    historyOverlay.style.top = "0";
    historyOverlay.style.left = "0";
    historyOverlay.style.width = "100%";
    historyOverlay.style.height = "100%";
    historyOverlay.style.background = "rgba(0,0,0,0.8)";
    historyOverlay.style.color = "white";
    historyOverlay.style.padding = "20px";
    historyOverlay.style.overflowY = "scroll";
    historyOverlay.style.zIndex = "1000";

    let historyContent = "<h2>Sales History</h2><button onclick='closeSalesHistory(this)'>Close</button>";

    salesHistory.forEach((sale, index) => {
        historyContent += `
            <div style="margin-bottom: 20px;">
                <h3>Sale #${index + 1}</h3>
                <p>Date: ${sale.date.toLocaleString()}</p>
                <p>Total: $${sale.total}</p>
                <p>Paid: $${sale.paid}</p>
                <p>Method: ${sale.method}</p>
                <table style="width: 100%; text-align: left; margin-top: 10px; border: 1px solid #fff;">
                    <thead>
                        <tr>
                            <th>Qty</th>
                            <th>Description</th>
                            <th>Price</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${sale.items
                            .map(
                                (item) =>
                                    `<tr>
                                        <td>${item.quantity}</td>
                                        <td>${item.description}</td>
                                        <td>${item.price}</td>
                                        <td>${item.total}</td>
                                    </tr>`
                            )
                            .join("")}
                    </tbody>
                </table>
            </div>
        `;
    });

    historyOverlay.innerHTML = historyContent;
    document.body.appendChild(historyOverlay);
}

// Close sales history overlay
function closeSalesHistory(button) {
    const overlay = button.parentElement;
    document.body.removeChild(overlay);
}

function completeSale() {
    $.ajax({
        url: '/salon/complete-sale/', // The endpoint for completing the sale
        type: 'POST', // HTTP method
        data: {
            sale_id: saleId,
            csrfmiddlewaretoken: getCSRFToken(), // Include the CSRF token in the data
        },
        success: function (response) {
            if (response.status === 'success') {
                alert('Sale has been marked as completed, you can now make payment.');
                // Optionally update the UI to reflect the completed status
            } else {
                console.log(saleId);
                if (!saleId) {
                    response.message = "You have not selected any item!";
                }
                alert('Error: ' + response.message);
            }
        },
        error: function (xhr, status, error) {
            console.error('Error:', error);
            alert('An error occurred while completing the sale.');
        }
    });
}
