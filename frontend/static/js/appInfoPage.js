let upVoteForm = document.forms.namedItem("upVoteForm");
let upVoteBtn = document.querySelector("#upVoteBtn");
let downVoteForm = document.forms.namedItem("downVoteForm");
let downVoteBtn = document.querySelector("#downVoteBtn");

makeFormAsync(upVoteForm, upVoteBtn, (res) => {
	upVoteBtn.lastElementChild.innerHTML = res["up_votes"];
	downVoteBtn.lastElementChild.innerHTML = res["down_votes"];
});

makeFormAsync(downVoteForm, downVoteBtn, (res) => {
	upVoteBtn.lastElementChild.innerHTML = res["up_votes"];
	downVoteBtn.lastElementChild.innerHTML = res["down_votes"];
});
