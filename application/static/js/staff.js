const staff = sessionStorage.getItem("staff");
if (!staff) {
  const pw = prompt("비밀번호를 입력해주세요.");
  const _hash = CryptoJS.SHA256("hati").toString();
  if (CryptoJS.SHA256(pw).toString() === _hash) {
    location.href = "/staff/shorten_url";
    sessionStorage.setItem("staff", "true");
  } else {
    alert("비밀번호가 일치하지 않습니다.");
    location.href = "/";
  }
}
