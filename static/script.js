// Grab the elements from the HTML
const mainForm = document.getElementById('mainForm');
const modal = document.getElementById('previewModal');

// 1. INTERCEPT THE FORM SUBMISSION
mainForm.addEventListener("submit", function(e) {
    // Stop the form from sending data to Python immediately
    e.preventDefault(); 

    // Get only the name value
    const nameValue = document.getElementById("student_name").value;

    // Inject the name into the Preview Modal text
    document.getElementById("previewName").innerText = nameValue;

    // Make the Modal visible (flex ensures centering)
    modal.style.display = "flex";
    
    console.log("Showing preview for: " + nameValue);
});

// 2. FUNCTION TO CLOSE THE MODAL (If they clicked "Edit")
function closePreview() {
    modal.style.display = "none";
}

// 3. FUNCTION FOR FINAL DOWNLOAD
function submitFinal() {
    const confirmBtn = document.querySelector(".btn-confirm");
    
    // Change button appearance to show progress
    confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    confirmBtn.style.background = "#95a5a6";
    confirmBtn.disabled = true;

    // Submit the form to the Python /generate route
    mainForm.submit();

    // Hide the modal and reset button after 4 seconds
    setTimeout(() => {
        modal.style.display = "none";
        confirmBtn.innerHTML = 'Download Certificate <i class="fas fa-download"></i>';
        confirmBtn.style.background = "#27ae60"; 
        confirmBtn.disabled = false;
    }, 4000);
}