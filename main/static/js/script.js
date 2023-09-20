

function form_visibility(show, div) {
    if(show) {
        document.getElementById(div).style.display = 'block'
    }
    else {
        document.getElementById(div).style.display = 'none'
        if (div == 'tournament-form') {
            const nameList = document.getElementById("input-container");
            nameList.innerHTML = "";
        }
    }
}


function create_inputs() {

    const divContainer = document.getElementById('input-container');

    const divInputGroup = document.createElement('div');
    divInputGroup.classList.add("input-group", "mb-1");

    const input1 = document.createElement("input");
    input1.type = "text";
    input1.name = `names`;
    input1.required = true;
    input1.placeholder = "Enter a name";
    input1.classList.add("form-control");

    const input2 = document.createElement("input");
    input2.type = "text";
    input2.name = `names`;
    input2.required = true;
    input2.placeholder = "Enter name";
    input2.classList.add("form-control");

    const removeButton = document.createElement('button');
    removeButton.type = "button";
    removeButton.classList.add("btn", 'btn-sm');

    removeButton.addEventListener("click", () => {
        divInputGroup.remove();
    });

    const removeImage = document.createElement("img");
    removeImage.src = "../static/images/icons/trash.png";
    removeImage.alt = "Remove";
    removeImage.width = 35;
    removeImage.height = 32;

    removeButton.appendChild(removeImage);

    divInputGroup.appendChild(input1);
    divInputGroup.appendChild(input2);
    divInputGroup.appendChild(removeButton);

    divContainer.appendChild(divInputGroup);

    document.getElementById('create-button').disabled = false;
}

function print_table_data(table_id) {
    
    if (table_id == 'table-print') {
        var htmlToPrint = '' +
        '<style type="text/css">' +
        'table {' +
        '    width: 100%;' +
        '    border-collapse: collapse;' +
        '    font-family: Arial, sans-serif;' +
        '}' +
        'table th, table td {' +
        '    border: 1px solid #000;' +
        '    padding: 2px;' +
        '    text-align: center;' +
        '}' +
        'table th {' +
        '    background-color: #f2f2f2;' +
        '}' +
        '</style>';
    }
    else {
        var htmlToPrint = '' +
    '<style type="text/css">' +
        'body {' +
        '    display: flex;' +
        '    justify-content: center;' +
        '    align-items: flex-start;' + // Aligns items at the start of the cross axis (top for column direction)
        '    height: 100vh;' +
        '    margin: 0;' +
        '}' +
        'table {' +
        '    width: auto;' +
        '    border-collapse: collapse;' +
        '    font-family: Arial, sans-serif;' +
        '}' +
        'table th, table td {' +
        '    border: 1px solid #000;' +
        '    padding-right: 15px;' +
        '    padding-left: 15px;' +
        '    padding-bottom: 7px;' +
        '    padding-top: 7px;' +
        '    text-align: center;' +
        '}' +
        'table th {' +
        '   background-color: #f2f2f2;' +
    '}' +
    '</style>';


    }

    div_table = document.getElementById(table_id)
    div_table.style.display = 'block'
    htmlToPrint += div_table.innerHTML
    div_table.style.display = 'none'
    const printWindow = window.open('', '_print-standing');
    printWindow.document.write(htmlToPrint);
    printWindow.document.close();
    printWindow.print();
}