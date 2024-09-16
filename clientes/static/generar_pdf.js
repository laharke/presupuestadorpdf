//Function que me permite agarrar el cookie para mandar fetchs con el csrf token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

function generar_pdf() {
    tableData = getTableData();
    empresa = $('#empresa').val()
    fetch('/generar_pdf', {
        method: 'POST',
        body: JSON.stringify({
            tableData: tableData,
            empresa: empresa  
        }),
    
        headers: {
            "X-CSRFToken": csrftoken
        }
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sample.pdf';
        document.body.appendChild(a); // Append <a> to body temporarily
        a.click();
        a.remove(); // Remove the element after downloading
    })
}

// Function to convert table data into JSON objects
function getTableData() {

    // Get the table by ID
    var table = document.getElementById('tablePdf');
    
    // Get all rows from the tbody
    var rows = table.getElementsByTagName('tbody')[0].rows;

    // Get column headers
    var headers = table.getElementsByTagName('thead')[0].rows[0].cells;
    var headerNames = Array.from(headers).map(header => header.innerText);

    // Array to hold JSON objects for each row
    var jsonData = [];

    // Iterate through each row
    for (var i = 0; i < rows.length; i++) {
        // Get all cells in the current row
        var cells = rows[i].cells; 
        var rowObject = {};

        // Create a JSON object with column headers as keys
        for (var j = 0; j < cells.length; j++) {
                if (cells[j].innerText != ""){
                rowObject[headerNames[j]] = cells[j].innerText; 
            }else{
              if (j == 3){
                  rowObject[headerNames[j]] = cells[j].children[0].checked
              }else{
                  rowObject[headerNames[j]] = cells[j].children[0].value;
              }
            }
        }

        // Add JSON object to array
        jsonData.push(rowObject); 
    }
    return jsonData;
}
