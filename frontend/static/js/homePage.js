let feedbackForm = document.forms.namedItem("feedbackForm");
let feedbackButton = document.querySelector("#feedbackButton");

feedbackForm.addEventListener("submit", async function (e) {
	e.preventDefault();
	let formData = new FormData(feedbackForm);
	let postData = {};
	formData.forEach((value, key) => (postData[key] = value));
	feedbackButton.disabled = true;
	feedbackButton.textContent = "Sending...";
	let res = await fetch(feedbackForm.action, {
		method: "POST",
		credentials: "same-origin",
		headers: {
			"X-CSRFToken": postData["csrfmiddlewaretoken"],
			Accept: "application/json",
			"Content-Type": "application/json",
		},
		body: JSON.stringify(postData),
	});
	if (res.status >= 400) {
		alert("Could not send request.");
	} else {
		res = await res.json();
		alert(res.message);
	}
	feedbackButton.textContent = "Send";
	feedbackButton.disabled = false;
	return false;
});
