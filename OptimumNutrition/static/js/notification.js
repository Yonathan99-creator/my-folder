document.addEventListener("DOMContentLoaded", function () {
    const button = document.getElementById("notification-button");
    const menu = document.getElementById("notification-menu");
    const countSpan = document.getElementById("notification-count");

    button.addEventListener("click", function (event) {
        menu.classList.toggle("opacity-0");
        menu.classList.toggle("invisible");
        event.stopPropagation();
    });

    document.addEventListener("click", function (event) {
        if (!menu.contains(event.target) && !button.contains(event.target)) {
            menu.classList.add("opacity-0", "invisible");
        }
    });

    const notificationMessages = menu.querySelectorAll('.notification-item');
    const notificationCount = notificationMessages.length;
    
    if (notificationCount > 0) {
        countSpan.textContent = notificationCount;
        countSpan.classList.remove('hidden');
    }

    notificationMessages.forEach(item => {
        const deleteButton = item.querySelector('.delete-button');
        deleteButton.addEventListener('click', () => {
            item.remove();
            updateNotificationCount();
        });
    });

    function updateNotificationCount() {
        const remainingItems = menu.querySelectorAll('.notification-item').length;
        if (remainingItems > 0) {
            countSpan.textContent = remainingItems;
        } else {
            countSpan.textContent = '0';
            countSpan.classList.add('hidden');
        }
    }
});