// modal for notifications
function openNotifModal() {
    document.getElementById('notifModal').style.display = 'block';
}

function closeNotifModal() {
    document.getElementById('notifModal').style.display = 'none';
}

// Close the modal if the user clicks outside of the modal content
window.onclick = function(event) {
    const modal = document.getElementById('notifModal');
    if (event.target === modal) {
        closeNotifModal();
    }
}
