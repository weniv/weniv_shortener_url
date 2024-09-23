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

if (copyBtn) {
  copyBtn.addEventListener("click", handleClipBoard);
}

// QR
const qrUrl = document.querySelector(".result span")?.textContent;
const qrcodeContainer = document.getElementById("qrcode");
const downloadButton = document.getElementById("downloadButton");

if (qrUrl) {
  qrcodeContainer.innerHTML = "";

  QRCode.toCanvas(qrUrl, { width: 240 }, function (error, canvas) {
    if (error) console.error(error);
    qrcodeContainer.appendChild(canvas);
  });

  downloadButton.addEventListener("click", () => {
    const canvas = qrcodeContainer.querySelector("canvas");

    if (canvas) {
      const image = canvas
        .toDataURL("image/png")
        .replace("image/png", "image/octet-stream");
      const link = document.createElement("a");
      link.download = "qrcode.png";
      link.href = image;
      link.click();
    }
  });
}

const staffLink = document.getElementById("staffLink");
if (staffLink) {
  staffLink.addEventListener("click", (e) => {
    e.preventDefault();

    const staff = sessionStorage.getItem("staff");
    if (staff) {
      location.href = "/staff/shorten_url";
      return;
    }
    const pw = prompt("비밀번호를 입력해주세요.");
    const _hash = CryptoJS.SHA256("hati").toString();
    if (CryptoJS.SHA256(pw).toString() === _hash) {
      location.href = "/staff/shorten_url";
      sessionStorage.setItem("staff", "true");
    } else {
      alert("비밀번호가 일치하지 않습니다.");
      location.href = "/";
    }
  });
}
