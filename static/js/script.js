let isPlaying = localStorage.getItem("isPlaying") === "true"; // ロード時に再生状態を取得
const music = document.getElementById("bg-music");
const musicButton = document.getElementById("music-button");
const musicIcon = document.getElementById("music-icon");

// 音楽再生状態を反映
window.addEventListener("DOMContentLoaded", () => {
    if (isPlaying) {
        music.play();
        updateButtonText(true);
    } else {
        updateButtonText(false);
    }
});

function toggleMusic() {
    isPlaying = !isPlaying;
    if (isPlaying) {
        music.play();
    } else {
        music.pause();
    }
    localStorage.setItem("isPlaying", isPlaying); // 状態を保存
    updateButtonText(isPlaying);
}

function updateButtonText(isPlaying) {
    if (isPlaying) {
        musicButton.textContent = "⏸ 音楽を停止";
        musicIcon.textContent = "⏸";
    } else {
        musicButton.textContent = "🎵 音楽を再生";
        musicIcon.textContent = "🎵";
    }
}

// "戻る"ボタンのクリックイベントをオーバーライド
// document.querySelector(".back-button").addEventListener("click", (event) => {
//     event.preventDefault(); // デフォルトの動作を停止
//     localStorage.setItem("isPlaying", isPlaying); // 状態を保存
//     history.back();
// });