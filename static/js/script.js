document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("task-form");

    form.addEventListener("submit", (e) => {
        const title = form.querySelector("input[name='title']").value;
        if (title.trim() === "") {
            e.preventDefault();
            alert("Por favor, insira um título para a tarefa.");
        }
    });
});
