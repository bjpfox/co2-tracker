// Event listener for basic form validation 
const submit_button = document.querySelector('.submit-btn') 
submit_button.addEventListener('click', function(event) {
    const input_fields = document.getElementsByTagName('input')
    let error_message = ""
    
    // Check input fields 
    for (const input of input_fields) {
        if (input.value === "") {
            error_message += `Please enter a value for your ${input.name}` + "<br>"
            event.preventDefault()
        }
    }
    // Check password length at least 6 chars
    const password_field = document.getElementById('password-input')
    if ((password_field != null) && (password_field.value.length < 6)) {
        error_message += "Please enter password with at least 6 characters<br>"
        event.preventDefault()
    }

    // Check passwords match
    const password_confirm = document.getElementById('password-confirm-input')
    if ((password_field != null) && (password_confirm != null) && (password_field.value != password_confirm.value)) {
        error_message += "Your passwords don't match!<br>"
        event.preventDefault()
    }

    // Check email valid
    const email_address = document.getElementById('email-input')
    pattern = new RegExp('[a-zA-Z0-9.]+@[a-zA-Z0-9.]+[.]+[a-zA-Z]+')
    // pattern = /a-zA-Z0-9.]+@[a-zA-Z0-9.]+[.]+[a-zA-Z]+'/
    // if ((email_address != null) && (len(email_address.value.match(pattern)) > 0)) {
    console.log(email_address.value)
    console.log(pattern)
    // console.log(pattern.test(email_address.value))
    if ((email_address != null) && (!pattern.test(email_address.value))) {
    // if ((email_address != null) && (!il_address.value.match(pattern))) {
        error_message += "Your email address is not valid. <br>" 
        event.preventDefault()
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
    
