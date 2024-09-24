
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






