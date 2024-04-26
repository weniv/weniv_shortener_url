// 페이지뷰 데이터 전송
fetch("https://www.analytics.weniv.co.kr/collect/pageview", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ url: window.location.href }),
})
  .then((response) => {
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    return response.json();
  })
  .then((data) => {
    sessionStorage.setItem("session_id", data.session_id);
  })
  .catch((error) => console.error("Error:", error));

// 앵커 클릭 이벤트 리스너 등록
document.addEventListener("click", function (event) {
  const ANCHOR = event.target.closest("a");
  if (ANCHOR) {
    event.preventDefault(); // 기본 동작 막기
    var session_id = sessionStorage.getItem("session_id");
    const source_url = window.location.href;
    const target_url = ANCHOR.href;
    const target_tar = ANCHOR.target || "_self";

    fetch("https://www.analytics.weniv.co.kr/collect/anchor-click", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Session-Id": session_id,
      },
      body: JSON.stringify({ source_url, target_url }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        window.open(target_url, target_tar);
      })
      .catch((error) => console.error("Error:", error));
  }
});
