// 페이지뷰 데이터 전송
const this_page_url = window.location.href;
let session_id = sessionStorage.getItem("session_id");

if (!session_id) {
  fetch("https://www.analytics.weniv.co.kr/collect/pageview", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url: this_page_url }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      sessionStorage.setItem("session_id", data.session_id);
      session_id = data.session_id;
    })
    .catch((error) => console.error("Error:", error));
}

// 클릭 데이터 전송
const sendAnalyticsClick = async (type, targetUrl = "", func) => {
  try {
    const response = await fetch(
      "https://www.analytics.weniv.co.kr/collect/anchor-click",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Session-Id": session_id,
        },
        body: JSON.stringify({
          source_url: this_page_url,
          target_url: targetUrl,
          type,
        }),
      }
    );
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
  } catch (error) {
    console.error("Error:", error);
  } finally {
    func && func();
  }
};

// URL 입력 후 submit 이벤트
const urlForm = document.getElementById("urlForm");
if (urlForm) {
  urlForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const inputUrl = e.currentTarget.querySelector("#original_url").value;

    const final = () => {
      e.target.submit();
    };
    sendAnalyticsClick("단축 URL 생성", inputUrl, final);
  });
}

// QR 이미지 다운로드 이벤트
if (downloadButton) {
  downloadButton.addEventListener("click", () => {
    const inputUrl = document.getElementById("originUrl").href;
    sendAnalyticsClick("QR 이미지 다운로드", inputUrl);
  });
}

// 다른 URL 이동 이벤트
const links = document.querySelectorAll(".a-click");
if (links.length > 0) {
  links.forEach((link) =>
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const inputUrl = e.currentTarget.href;
      const text = e.currentTarget.querySelector("img").alt;
      const final = () => {
        window.open(inputUrl, "_blank");
      };
      sendAnalyticsClick(text, inputUrl, final);
    })
  );
}
