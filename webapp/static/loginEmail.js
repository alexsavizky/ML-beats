
document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission
    const formData = new FormData(event.target); // Create a FormData object from the form
    const email = formData.get('email'); // Get the email
    const password = formData.get('password'); // Get the password
    var errorMessageDiv = document.getElementById('errorMessage');

    // Prepare the data to be sent in JSON format
    const data = {
        email: email,
        password: password
    };

    fetch('/login_email', {
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
