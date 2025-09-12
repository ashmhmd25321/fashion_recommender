// Rating stars functionality
document.addEventListener('DOMContentLoaded', function() {
    // Handle star rating selection
    const stars = document.querySelectorAll('.rating-form .star');
    const ratingInput = document.getElementById('rating-value');
    
    if (stars.length > 0 && ratingInput) {
        stars.forEach(star => {
            star.addEventListener('click', function() {
                const value = this.getAttribute('data-value');
                ratingInput.value = value;
                
                // Update visual state
                stars.forEach(s => {
                    if (s.getAttribute('data-value') <= value) {
                        s.classList.add('active');
                    } else {
                        s.classList.remove('active');
                    }
                });
            });
        });
    }
    
    // Handle AJAX voting
    const voteForm = document.getElementById('ajax-vote-form');
    if (voteForm) {
        voteForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const itemId = this.getAttribute('data-item-id');
            const voteValue = document.getElementById('rating-value').value;
            const comment = document.getElementById('comment').value;
            
            fetch(`/api/vote/${itemId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    value: voteValue,
                    comment: comment
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the UI
                    document.getElementById('vote-score').textContent = data.new_score.toFixed(1);
                    document.getElementById('votes-count').textContent = data.votes_count;
                    
                    // Show success message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-success';
                    alertDiv.textContent = data.message;
                    
                    const formContainer = document.querySelector('.form-container');
                    formContainer.insertBefore(alertDiv, formContainer.firstChild);
                    
                    // Remove alert after 3 seconds
                    setTimeout(() => {
                        alertDiv.remove();
                    }, 3000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
    
    // Image preview for upload
    const imageInput = document.getElementById('image-upload');
    const imagePreview = document.getElementById('image-preview');
    
    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                }
                reader.readAsDataURL(file);
            }
        });
    }
}); 