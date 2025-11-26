/**
 * NANOTRONICS SURVEY - JavaScript
 * Interactive survey functionality
 */

// State management
let currentQuestion = 1;
const totalQuestions = 11;
const surveyData = {};

// DOM Elements
const welcomeScreen = document.getElementById('welcome-screen');
const surveyScreen = document.getElementById('survey-screen');
const thankyouScreen = document.getElementById('thankyou-screen');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const submitBtn = document.getElementById('submit-btn');

/**
 * Start the survey
 */
function startSurvey() {
    welcomeScreen.classList.remove('active');
    surveyScreen.classList.add('active');
    showQuestion(1);
}

/**
 * Show a specific question
 */
function showQuestion(questionNum) {
    // Hide all questions
    document.querySelectorAll('.question-card').forEach(card => {
        card.classList.remove('active');
    });
    
    // Show the current question
    const currentCard = document.querySelector(`.question-card[data-question="${questionNum}"]`);
    if (currentCard) {
        currentCard.classList.add('active');
    }
    
    // Update progress
    updateProgress(questionNum);
    
    // Update navigation buttons
    updateNavButtons(questionNum);
    
    currentQuestion = questionNum;
}

/**
 * Update progress bar
 */
function updateProgress(questionNum) {
    const percentage = (questionNum / totalQuestions) * 100;
    progressFill.style.width = `${percentage}%`;
    progressText.textContent = `${questionNum} de ${totalQuestions}`;
}

/**
 * Update navigation buttons visibility
 */
function updateNavButtons(questionNum) {
    prevBtn.disabled = questionNum === 1;
    
    if (questionNum === totalQuestions) {
        nextBtn.style.display = 'none';
        submitBtn.style.display = 'inline-flex';
    } else {
        nextBtn.style.display = 'inline-flex';
        submitBtn.style.display = 'none';
    }
}

/**
 * Go to next question
 */
function nextQuestion() {
    if (currentQuestion < totalQuestions) {
        saveCurrentAnswer();
        showQuestion(currentQuestion + 1);
        scrollToTop();
    }
}

/**
 * Go to previous question
 */
function prevQuestion() {
    if (currentQuestion > 1) {
        saveCurrentAnswer();
        showQuestion(currentQuestion - 1);
        scrollToTop();
    }
}

/**
 * Scroll to top of container smoothly
 */
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Save current question's answer
 */
function saveCurrentAnswer() {
    const currentCard = document.querySelector(`.question-card[data-question="${currentQuestion}"]`);
    if (!currentCard) return;
    
    // Collect radio inputs
    const radioInputs = currentCard.querySelectorAll('input[type="radio"]:checked');
    radioInputs.forEach(input => {
        surveyData[input.name] = input.value;
    });
    
    // Collect checkbox inputs
    const checkboxInputs = currentCard.querySelectorAll('input[type="checkbox"]:checked');
    checkboxInputs.forEach(input => {
        if (!surveyData[input.name]) {
            surveyData[input.name] = [];
        }
        if (!surveyData[input.name].includes(input.value)) {
            surveyData[input.name].push(input.value);
        }
    });
    
    // Collect text inputs
    const textInputs = currentCard.querySelectorAll('textarea, input[type="text"]');
    textInputs.forEach(input => {
        if (input.value.trim()) {
            surveyData[input.name] = input.value.trim();
        }
    });
    
    // Collect range inputs
    const rangeInputs = currentCard.querySelectorAll('input[type="range"]');
    rangeInputs.forEach(input => {
        surveyData[input.name] = input.value;
    });
    
    // Collect hidden inputs (for star rating)
    const hiddenInputs = currentCard.querySelectorAll('input[type="hidden"]');
    hiddenInputs.forEach(input => {
        if (input.value) {
            surveyData[input.name] = input.value;
        }
    });
}

/**
 * Submit the survey
 */
async function submitSurvey() {
    saveCurrentAnswer();
    
    // Collect selected tags
    document.querySelectorAll('.tag-btn.selected, .word-btn.selected').forEach(btn => {
        const questionCard = btn.closest('.question-card');
        const questionNum = questionCard.dataset.question;
        const key = `q${questionNum}_tags`;
        if (!surveyData[key]) {
            surveyData[key] = [];
        }
        surveyData[key].push(btn.dataset.value);
    });
    
    // Add timestamp
    surveyData.timestamp = new Date().toISOString();
    
    console.log('Survey Data:', surveyData);
    
    // Show loading state
    submitBtn.classList.add('loading');
    
    try {
        // Try to send to backend
        const response = await fetch('/api/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(surveyData),
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        showThankYou();
    } catch (error) {
        console.log('Backend not available, saving locally');
        // Save to localStorage as fallback
        saveToLocalStorage(surveyData);
        showThankYou();
    }
}

/**
 * Save to localStorage as fallback
 */
function saveToLocalStorage(data) {
    const surveys = JSON.parse(localStorage.getItem('nanotronics_surveys') || '[]');
    surveys.push(data);
    localStorage.setItem('nanotronics_surveys', JSON.stringify(surveys));
}

/**
 * Show thank you screen
 */
function showThankYou() {
    surveyScreen.classList.remove('active');
    thankyouScreen.classList.add('active');
    submitBtn.classList.remove('loading');
}

/**
 * Initialize interactive elements
 */
function initInteractiveElements() {
    // Tag buttons (single select)
    document.querySelectorAll('.quick-tags:not(.multi-select) .tag-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            // Deselect siblings
            this.parentElement.querySelectorAll('.tag-btn').forEach(sibling => {
                sibling.classList.remove('selected');
            });
            this.classList.add('selected');
            
            // Also update the textarea if it has the same question
            const questionCard = this.closest('.question-card');
            const textarea = questionCard.querySelector('textarea');
            if (textarea && !textarea.value) {
                textarea.value = this.dataset.value;
            }
        });
    });
    
    // Tag buttons (multi select)
    document.querySelectorAll('.quick-tags.multi-select .tag-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            this.classList.toggle('selected');
        });
    });
    
    // Word cloud buttons
    document.querySelectorAll('.word-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            // Single select for word cloud
            this.parentElement.querySelectorAll('.word-btn').forEach(sibling => {
                sibling.classList.remove('selected');
            });
            this.classList.add('selected');
            
            // Update textarea
            const questionCard = this.closest('.question-card');
            const textarea = questionCard.querySelector('textarea');
            if (textarea) {
                textarea.value = this.dataset.value;
            }
        });
    });
    
    // Star rating
    document.querySelectorAll('.star-rating').forEach(container => {
        const stars = container.querySelectorAll('.star');
        const hiddenInput = container.querySelector('input[type="hidden"]');
        
        stars.forEach(star => {
            star.addEventListener('click', function() {
                const value = parseInt(this.dataset.value);
                hiddenInput.value = value;
                
                stars.forEach((s, index) => {
                    if (index < value) {
                        s.classList.add('active');
                    } else {
                        s.classList.remove('active');
                    }
                });
            });
            
            star.addEventListener('mouseenter', function() {
                const value = parseInt(this.dataset.value);
                stars.forEach((s, index) => {
                    if (index < value) {
                        s.style.color = 'var(--accent-yellow)';
                    } else {
                        s.style.color = '';
                    }
                });
            });
            
            star.addEventListener('mouseleave', function() {
                stars.forEach(s => {
                    if (!s.classList.contains('active')) {
                        s.style.color = '';
                    }
                });
            });
        });
    });
    
    // Slider value display
    document.querySelectorAll('.slider').forEach(slider => {
        slider.addEventListener('input', function() {
            // Visual feedback could be added here
        });
    });
    
    // Reset checkboxes when "Todo está bien" is selected (Question 5)
    const nothingCheckbox = document.querySelector('input[value="nada"]');
    if (nothingCheckbox) {
        nothingCheckbox.addEventListener('change', function() {
            if (this.checked) {
                const siblings = this.closest('.checkbox-grid').querySelectorAll('input[type="checkbox"]');
                siblings.forEach(cb => {
                    if (cb !== this) {
                        cb.checked = false;
                    }
                });
            }
        });
    }
    
    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (surveyScreen.classList.contains('active')) {
            if (e.key === 'ArrowRight' || e.key === 'Enter') {
                if (currentQuestion < totalQuestions) {
                    nextQuestion();
                }
            } else if (e.key === 'ArrowLeft') {
                if (currentQuestion > 1) {
                    prevQuestion();
                }
            }
        }
    });
}

/**
 * Handle textarea auto-clear on tag/word selection
 */
function initTextareaSync() {
    document.querySelectorAll('.tag-btn, .word-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const questionCard = this.closest('.question-card');
            const textarea = questionCard.querySelector('textarea');
            if (textarea && !this.classList.contains('selected')) {
                // Clear textarea when using quick options
                // Only if user hasn't typed something else
            }
        });
    });
}

/**
 * Touch support for mobile
 */
function initTouchSupport() {
    let touchStartX = 0;
    let touchEndX = 0;
    
    surveyScreen.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    
    surveyScreen.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }, { passive: true });
    
    function handleSwipe() {
        const swipeThreshold = 100;
        const diff = touchStartX - touchEndX;
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0 && currentQuestion < totalQuestions) {
                // Swipe left - next question
                nextQuestion();
            } else if (diff < 0 && currentQuestion > 1) {
                // Swipe right - previous question
                prevQuestion();
            }
        }
    }
}

/**
 * Analytics tracking (placeholder)
 */
function trackEvent(eventName, data = {}) {
    console.log('Event:', eventName, data);
    // Can be connected to Google Analytics, Mixpanel, etc.
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initInteractiveElements();
    initTextareaSync();
    initTouchSupport();
    
    // Track survey start
    document.querySelector('.btn-primary')?.addEventListener('click', function() {
        trackEvent('survey_started');
    });
});

// Make functions globally available
window.startSurvey = startSurvey;
window.nextQuestion = nextQuestion;
window.prevQuestion = prevQuestion;
window.submitSurvey = submitSurvey;

