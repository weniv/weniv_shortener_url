// 복사
let copyBtn = document.getElementById("copyBtn");

const handleClipBoard = async (e) => {
  const text = e.currentTarget.previousElementSibling.innerText;

  const TIME = 1500;

  const copyBtnContent = (type) => {
    copyBtn.querySelector("img").src = `/static/img/${type}.svg`;
    copyBtn.querySelector("span").innerText =
      type === "copy" ? "복사" : `복사완료`;
  };

  copyBtn.classList.add("click");

  if (navigator.clipboard) {
    try {
      await navigator.clipboard.writeText(text);

      copyBtnContent("check");

      setTimeout(() => {
        copyBtn.classList.remove("click");
        copyBtnContent("copy");
      }, TIME);
    } catch (e) {
      alert("실패하였습니다. 다시 시도해주세요.");
    }
  } else {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.top = 0;
    textarea.style.left = 0;
    textarea.style.position = "fixed";

    // 흐름 4.
    document.body.appendChild(textarea);
    // focus() -> 사파리 브라우저 서포팅
    textarea.focus();
    // select() -> 사용자가 입력한 내용을 영역을 설정할 때 필요
    textarea.select();
    // 흐름 5.
    document.execCommand("copy");
    // 흐름 6.
    document.body.removeChild(textarea);

    copyBtnContent("check");

    setTimeout(() => {
      copyBtn.classList.remove("click");
      copyBtnContent("copy");
    }, TIME);
  }
};

copyBtn.addEventListener("click", handleClipBoard);

// QR
const qrUrl = document.querySelector(".result span").textContent;
const qrcodeContainer = document.getElementById("qrcode");
qrcodeContainer.innerHTML = "";

QRCode.toCanvas(qrUrl, { width: 240 }, function (error, canvas) {
  if (error) console.error(error);
  qrcodeContainer.appendChild(canvas);
});
