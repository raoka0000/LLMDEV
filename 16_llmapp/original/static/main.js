window.onload = function () {
    const chatBox = document.getElementById('chat-box');
    const form = document.getElementById('chat-form');
    const characterInput = document.getElementById('character-input');
    const textarea = document.getElementById('user-input');
    const submitButton = document.getElementById('submit-button');

    // チャットボックスを一番下までスクロール
    if (chatBox) {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // キャラクター名が空のときはメッセージ入力欄と送信ボタンを無効化
    function updateInputState() {
        const hasCharacter = characterInput.value.trim().length > 0;
        textarea.disabled = !hasCharacter;
        submitButton.disabled = !hasCharacter;
        textarea.placeholder = hasCharacter
            ? 'メッセージを入力...'
            : 'まずキャラクター名を入力してください';
    }

    characterInput.addEventListener('input', updateInputState);
    updateInputState();

    // Ctrl + Enterでフォームを送信
    textarea.addEventListener('keydown', function (event) {
        if (event.ctrlKey && event.key === 'Enter') {
            event.preventDefault();
            if (!textarea.disabled && textarea.value.trim().length > 0) {
                form.submit();
            }
        }
    });

    // 送信時、キャラ名またはメッセージが空なら送信をブロック
    form.addEventListener('submit', function (event) {
        if (
            characterInput.value.trim().length === 0 ||
            textarea.value.trim().length === 0
        ) {
            event.preventDefault();
        }
    });
};
