function makeFormAsync(form, btn, callBack) {
	form.addEventListener("submit", async function (e) {
		e.preventDefault();
		let formData = new FormData(form);
		btn.disabled = true;
		let res = await fetch(form.action, {
			method: "POST",
			credentials: "same-origin",
			headers: {
				"X-CSRFToken": formData["csrfmiddlewaretoken"],
			},
			body: formData,
		});
		res = await res.json();
		alert(res.message);
		btn.disabled = false;
		callBack(res);
		return false;
	});
}
