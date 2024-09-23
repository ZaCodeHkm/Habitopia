
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


