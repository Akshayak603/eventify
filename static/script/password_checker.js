document.addEventListener('DOMContentLoaded', function(){
    // visible update password
    document.getElementById('toggle_password_update').addEventListener('click', function(){
        let passwordInput = document.getElementById('password_update');
        passwordInput.type = passwordInput.type === 'password' ? 'text' : 'passsword'; 
    })

    // visible confirm password
    document.getElementById('toggle_password_confirm').addEventListener('click', function(){
        let confirmInput = document.getElementById('password_confirm')
        confirmInput.type = confirmInput.type === 'password' ? 'text' : 'password'
    })

    // check for match
    document.getElementById('reset_password_form').addEventListener('submit', function(){
        let password_value = document.getElementById('password_update').value
        let confirm_value = document.getElementById('password_confirm').value
        
        if( password_value !== confirm_value){
            document.getElementById('password_mismatch').style.display = 'block';
            event.preventDefault();
        }
    })


})