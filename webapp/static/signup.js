
document.getElementById('signup-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission
    const formData = new FormData(event.target); // Create a FormData object from the form
    const email = formData.get('email'); // Get the email
    const password = formData.get('password'); // Get the password
    const first_name = formData.get('first_name');
    const last_name = formData.get('last_name');
    const passwordReapet = formData.get('passwordRepeat');
    var errorMessageDiv = document.getElementById('errorMessage');

    if ( password !==passwordReapet){
        errorMessageDiv.textContent = 'Passwords do not match.';
        return;
    }
    else{
        errorMessageDiv.textContent = '';
    }
    // Prepare the data to be sent in JSON format
    const data = {
        email: email,
        password: password,
        first_name: first_name,
        last_name : last_name
    };

    fetch('/signup_email', {
        method: 'POST', // Specify the method
        headers: {
            'Content-Type': 'application/json', // Specify the content type as JSON
        },
        body: JSON.stringify(data), // Convert the JavaScript object to a JSON string
    })
    .then(response => response.json()) // Parse the JSON response
    .then(data => {
        if (data.status === 'success'){
            console.log('Success:', data);
            window.location.href = '/main';
        }else{
            errorMessageDiv.textContent = 'There is already a user with this email.'
        }

        // Handle success. For example, redirecting to another page or showing a success message
    })
    .catch((error) => {

        console.error('Error:', error);
        // Handle errors here, such as showing an error message to the user
    });
});
