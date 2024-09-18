
$.ajax({
    type: 'POST',
    url: '/complete_habit/' + habit_id,
    success: function(data) {
      if (data.checked) {
        // update the template to display "hi"
      } else {
        // update the template to display "bye"
      }
    }
  });

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

// notifications

// Function to fetch notifications and display them in a custom modal
function fetchNotifications() {
    fetch('/notifications')
        .then(response => response.json())
        .then(data => {
            if (data.notifications && data.notifications.length > 0) {
                const modal = document.getElementById('notificationModal');
                const messageElement = document.getElementById('notificationMessage');
                
                // Display all notifications in the modal
                let notificationText = data.notifications.join('<br>');
                messageElement.innerHTML = notificationText;
                
                // Show the modal
                modal.style.display = 'block';
            }
        })
        .catch(error => console.error('Error fetching notifications:', error));
}

// Call the function when the page loads for the first time
window.onload = function() {
    // Check if this is the user's first visit to the page in this session
    if (!sessionStorage.getItem('firstVisit')) {
        fetchNotifications();
        sessionStorage.setItem('firstVisit', 'true'); // Set flag to prevent popups on reload
    }
};

// Close the modal when the user clicks on the "x"
const closeModalButton = document.getElementsByClassName('close')[0];
closeModalButton.onclick = function() {
    const modal = document.getElementById('notificationModal');
    modal.style.display = 'none';
};

// Close the modal if the user clicks outside of the modal
window.onclick = function(event) {
    const modal = document.getElementById('notificationModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
};