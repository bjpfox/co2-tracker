// Event listener for basic form validation 
const submit_button = document.querySelector('.submit-btn') 
submit_button.addEventListener('click', function(event) {
    const input_fields = document.getElementsByTagName('input')
    let error_message = ""
    
    // Check input fields 
    for (const input of input_fields) {
        if (input.value === "") {
            error_message += `Please enter a valid ${input.name}` + "<br>"
            event.preventDefault()
        }
    }

    // Check radio buttons, if any on page
    const radio_buttons = document.getElementsByClassName('radio-btn')
    if (radio_buttons.len > 0) {
        radioButtonSelected = false 
        for (const button of radio_buttons) {
            if (button.checked) {
                radioButtonSelected = true 
            }
        }
        if (!radioButtonSelected) {
            error_message += "Please select an option for interval <br>"
            event.preventDefault()
        }
    }

    const error_message_div = document.getElementById('error_message_div')
    error_message_div.innerHTML = error_message
})
    
