let addAppForm = document.forms.namedItem("addAppForm");
let addAppButton = document.querySelector("#addAppButton");

addAppForm.addEventListener("submit", async function (e) {
	e.preventDefault();
	let formData = new FormData(addAppForm);
	let postData = {};
	formData.forEach((value, key) => (postData[key] = value));
	let appLink = postData["app_playstore_link"];
	let appIdIdx = appLink.indexOf("id=");
	if (appIdIdx >= 0) {
		let appId = appLink.slice(appIdIdx + 3);
		addAppButton.disabled = true;
		addAppButton.textContent = "Sending...";
		let res = await fetch("api/app/" + appId, {
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
		addAppButton.textContent = "Send";
		addAppButton.disabled = false;
	} else {
		alert("Please Enter A Valid Playstore App Link");
	}
	return false;
});
