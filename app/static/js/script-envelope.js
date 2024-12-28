$(document).ready(function(){
	$('.leads').on('click',function(){
		const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
		var request = new XMLHttpRequest();
		var user = "{{ user.username }}"; // Correctly interpolate the Django variable
		var pk = "{{lead.pk}}"
		alert(pk)
		request.open("POST", "http://127.0.0.1:8000/accounts/login/" + user + "/", false);
		request.setRequestHeader("X-CSRFToken", csrftoken);
		request.onload = function () {
			if (request.status === 200) {
				// All images were successfully uploaded
				window.location.href = "http://127.0.0.1:8000/accounts/login/" + user + "/estoque-veiculos/";
			} else {
				console.error("Error uploading images");
			}
		};
		request.send(formData);
	})
})