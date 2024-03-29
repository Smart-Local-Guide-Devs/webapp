for (const votingForm of document.querySelectorAll(".votingForm")) {
	const upVoteForm = votingForm.querySelector(".upVoteForm");
	const upVoteBtn = votingForm.querySelector(".upVoteBtn");
	const downVoteForm = votingForm.querySelector(".downVoteForm");
	const downVoteBtn = votingForm.querySelector(".downVoteBtn");
	makeFormAsync(upVoteForm, upVoteBtn, (res) => {
		upVoteBtn.lastElementChild.innerText = res.up_votes;
		downVoteBtn.lastElementChild.innerText = res.down_votes;
	});
	makeFormAsync(downVoteForm, downVoteBtn, (res) => {
		upVoteBtn.lastElementChild.innerText = res.up_votes;
		downVoteBtn.lastElementChild.innerText = res.down_votes;
	});
}

for (let deleteReviewForm of document.querySelectorAll(".deleteReviewForm")) {
	let deleteReviewBtn = deleteReviewForm.querySelector(".deleteReviewBtn");
	makeFormAsync(deleteReviewForm, deleteReviewBtn, (res) => {
		if (res.status == 200) {
			deleteReviewForm.parentElement.parentElement.remove();
		}
	});
}
