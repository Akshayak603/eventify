function validate_date() {
    let start_date_evt = new Date(document.getElementById('start_date').value);
    let end_date_evt = new Date(document.getElementById('end_date').value);
    let today_date = new Date();
    
    if(today_date > start_date_evt){
        alert("Start date must be greater than or equal to today's date.");
        return false;
    }

    if(start_date_evt > end_date_evt){
        alert("End date must be greater than start date.");
        return false;
    }

    return true;

}

// function showAlert(message) {
//     container.innerHTML= `<div class="alert alert-warning alert-dismissible fade show" role="alert">
//     <strong>${message}</strong> 
//     </button>
//   </div>`
// }