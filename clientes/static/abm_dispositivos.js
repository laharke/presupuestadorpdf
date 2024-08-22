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

function editDispositivo(id, nombre, precio, pagoUnico){
    console.log('abro modal con los datos del dis')
    
    $('#idEdicion').val(id);
    $('#nameEdicion').val(nombre);
    $('#precioEdicion').val(precio);

    if (pagoUnico == 'True'){
        $('#pagoUnicoEdicion').prop('checked', true);
    }

    $('#modalEdicion').modal('show');

    //$('#modalEdicion').modal('hide');


}

function borrarDispositivo(id){
     
    fetch('/borrar_dispositivo', {
        method: 'POST',
        body:JSON.stringify({'id':id}),
        headers: {
            "X-CSRFToken": csrftoken
        }
    })
    .then(response => {
        //Handelas la RESPONSE
        return response.json()
    })
    .then(data => {
        if (data['result'] == 'ok'){
            location.href = location.href;
        }else{
            showAlert('error', 'No se puede borrar')
        }
    })

}