document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.calendar-box').forEach(box => {
        updateBoxAppearance(box); // This already attempts to set the right colors based on data attributes
    });
});

function updateBoxAppearance(box) {
    const isChecked = box.dataset.checked === 'true';
    const color = box.dataset.color;
    
    box.style.backgroundColor = isChecked ? color : 'white';
    box.classList.toggle('checked', isChecked);
}

function toggleBox(box) {
    const habitId = box.dataset.habitId;
    const date = box.dataset.date;
    const currentChecked = box.dataset.checked === 'true';
    const newChecked = !currentChecked;

    // Update local state
    box.dataset.checked = newChecked.toString();
    updateBoxAppearance(box);

    // Send update to server
    fetch(`/toggle_check/${habitId}/${date}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ checked: newChecked }),
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            // Revert if server update failed
            box.dataset.checked = currentChecked.toString();
            updateBoxAppearance(box);
        }
        console.log('Server response:', data);
    })
    .catch(error => {
        console.error('Error:', error);
        // Revert on error
        box.dataset.checked = currentChecked.toString();
        updateBoxAppearance(box);
    });
}

// Modal

function openModal() {
    document.getElementById('addHabitModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('addHabitModal').style.display = 'none';
}

// Close the modal if the user clicks outside of the modal content
window.onclick = function(event) {
    const modal = document.getElementById('addHabitModal');
    if (event.target === modal) {
        closeModal();
    }
}

//Diary Modal

function openModal2() {
    document.getElementById('diaryModal').style.display = 'block';
}

function closeModal2() {
    document.getElementById('diaryModal').style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('diaryModal');
    if (event.target === modal) {
        closeModal2();
    }
}

// Tab Functionality
function openTab(evt, tabName) {
    var i, tabcontent, tablinks;

    tabcontent = document.getElementsByClassName("tabcontent-detail");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";  
    }

    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    document.getElementById(tabName).style.display = "block";  
    evt.currentTarget.className += " active";
}

// Modal for Diary
function openDiaryModal() {
    document.getElementById('diaryModal').style.display = 'block';
}

function closeDiaryModal() {
    document.getElementById('diaryModal').style.display = 'none';
}

// Close the modal if the user clicks outside of the modal content
window.onclick = function(event) {
    const diaryModal = document.getElementById('diaryModal');
    if (event.target === diaryModal) {
        closeDiaryModal();
    }
}