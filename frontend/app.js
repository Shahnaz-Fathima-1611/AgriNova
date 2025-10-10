// Application data
const appData = {
  weatherData: {
    temperature: 22,
    humidity: 70,
    rainfall: 5,
    windSpeed: 5,
    location: "Agricultural Region"
  },
  riskData: {
    currentRisk: 0.73,
    riskLevel: "High Risk",
    recommendation: "Warning: High aphid risk predicted. Consider deploying biocontrol agents within 48 hours",
    monthlyTrend: [
      {"month": "Jan", "risk": 0.2},
      {"month": "Feb", "risk": 0.25},
      {"month": "Mar", "risk": 0.4},
      {"month": "Apr", "risk": 0.6},
      {"month": "May", "risk": 0.8},
      {"month": "Jun", "risk": 0.9},
      {"month": "Jul", "risk": 0.7},
      {"month": "Aug", "risk": 0.6},
      {"month": "Sep", "risk": 0.5},
      {"month": "Oct", "risk": 0.3},
      {"month": "Nov", "risk": 0.2},
      {"month": "Dec", "risk": 0.15}
    ]
  },
  newsAlerts: [
    {
      id: 1,
      title: "Unseasonal Rains Forecast for Next Week",
      date: "2024-01-15",
      priority: "High Priority",
      content: "Weather services predict unexpected rainfall patterns that may affect crop protection schedules. Farmers are advised to adjust their pesticide applications accordingly.",
      category: "weather"
    },
    {
      id: 2,
      title: "Aphid Outbreak Spotted in Nearby County",
      date: "2024-01-12",
      priority: "High Priority",
      content: "Local agricultural extension office reports significant aphid activity in neighboring regions.",
      category: "pest"
    }
  ],
  pesticideSchedule: [
    {
      date: "2024-01-16",
      targetPest: "Aphids",
      treatment: "Neem Oil",
      quantity: "5ml/L",
      area: "Field A (2.5 ha)",
      status: "Planned"
    },
    {
      date: "2024-01-22",
      targetPest: "Thrips",
      treatment: "Insecticidal Soap",
      quantity: "15ml/L",
      area: "Greenhouse 1",
      status: "Planned"
    },
    {
      date: "2024-01-25",
      targetPest: "Spider Mites",
      treatment: "Predatory Mites",
      quantity: "2000 units",
      area: "Field B (1.8 ha)",
      status: "Planned"
    }
  ],
  recentApplications: [
    {
      date: "2024-01-10",
      targetPest: "Whiteflies",
      treatment: "Yellow Sticky Traps",
      quantity: "20 traps",
      area: "Greenhouse 2",
      status: "Completed"
    }
  ],
  aiRecommendations: [
    "For upcoming aphid risk (85% probability), consider applying Neem Oil at 5ml/L concentration within the next 48 hours.",
    "Weather conditions favor thrips development. Deploy blue sticky traps as monitoring tools in addition to scheduled treatments.",
    "Beneficial insect populations are increasing. Consider reducing chemical applications and focusing on biological control methods."
  ]
};

// Global variables
let riskChart = null;
let currentRiskData = { ...appData.riskData };

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
  initializeApp();
});

// Initialize application
function initializeApp() {
  setupNavigation();
  setupSliders();
  setupRiskAssessment();
  initializeChart();
  populateNewsSection();
  populatePesticideSection();
  setupForms();
  setupModalHandlers();
  setupScheduleHandlers(); // Add this line
  
  // Show home section by default
  showSection('home');
}

// Schedule handlers
function setupScheduleHandlers() {
  // Add Schedule button
  const addScheduleBtn = document.getElementById('add-schedule-btn');
  if (addScheduleBtn) {
    addScheduleBtn.addEventListener('click', openAddScheduleModal);
  }
  
  // Close modal button
  const closeModalBtn = document.querySelector('#add-schedule-modal .close-modal');
  if (closeModalBtn) {
    closeModalBtn.addEventListener('click', closeAddScheduleModal);
  }
  
  // Add Schedule form submission
  const addScheduleForm = document.getElementById('add-schedule-form');
  if (addScheduleForm) {
    addScheduleForm.addEventListener('submit', handleAddScheduleForm);
  }
  
  // Close modal when clicking outside
  const scheduleModal = document.getElementById('add-schedule-modal');
  if (scheduleModal) {
    scheduleModal.addEventListener('click', function(e) {
      if (e.target === scheduleModal) {
        closeAddScheduleModal();
      }
    });
  }
}

function openAddScheduleModal() {
  const modal = document.getElementById('add-schedule-modal');
  if (modal) {
    modal.classList.remove('hidden');
  }
}

function closeAddScheduleModal() {
  const modal = document.getElementById('add-schedule-modal');
  if (modal) {
    modal.classList.add('hidden');
  }
}

function handleAddScheduleForm(e) {
  e.preventDefault();
  
  // Get form data
  const formData = {
    date: document.getElementById('schedule-date').value,
    targetPest: document.getElementById('schedule-pest').value,
    treatment: document.getElementById('schedule-treatment').value,
    quantity: document.getElementById('schedule-quantity').value,
    area: document.getElementById('schedule-area').value,
    status: 'Planned'
  };
  
  // Add to schedule
  appData.pesticideSchedule.push(formData);
  
  // Update the table
  populateScheduleTable();
  
  // Close modal and reset form
  closeAddScheduleModal();
  document.getElementById('add-schedule-form').reset();
  
  // Show success message
  showSuccessMessage('Schedule added successfully!');
}

// Navigation functionality
function setupNavigation() {
  const navLinks = document.querySelectorAll('.nav-link');
  
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const targetSection = this.getAttribute('href').substring(1);
      
      if (targetSection === 'login') {
        openLoginModal();
        return;
      }
      
      navigateToSection(targetSection);
    });
  });
}

function navigateToSection(sectionId) {
  // Update active nav link
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('href') === `#${sectionId}`) {
      link.classList.add('active');
    }
  });
  
  showSection(sectionId);
}

function showSection(sectionId) {
  // Hide all sections
  document.querySelectorAll('.section').forEach(section => {
    section.classList.remove('active');
  });
  
  // Show target section
  const targetSection = document.getElementById(sectionId);
  if (targetSection) {
    targetSection.classList.add('active');
  }
  
  // Initialize chart when pest-risk section is shown
  if (sectionId === 'pest-risk' && !riskChart) {
    setTimeout(initializeChart, 100);
  }
}

// Slider functionality
function setupSliders() {
  const sliders = [
    { id: 'temperature', valueId: 'temp-value', unit: '°C' },
    { id: 'humidity', valueId: 'humidity-value', unit: '%' },
    { id: 'rainfall', valueId: 'rainfall-value', unit: 'mm' },
    { id: 'windspeed', valueId: 'wind-value', unit: 'km/h' }
  ];
  
  sliders.forEach(slider => {
    const element = document.getElementById(slider.id);
    const valueElement = document.getElementById(slider.valueId);
    
    if (element && valueElement) {
      element.addEventListener('input', function() {
        valueElement.textContent = this.value;
        updateEnvironmentalData(slider.id, parseFloat(this.value));
      });
    }
  });
}

function updateEnvironmentalData(parameter, value) {
  switch(parameter) {
    case 'temperature':
      appData.weatherData.temperature = value;
      break;
    case 'humidity':
      appData.weatherData.humidity = value;
      break;
    case 'rainfall':
      appData.weatherData.rainfall = value;
      break;
    case 'windspeed':
      appData.weatherData.windSpeed = value;
      break;
  }
}

// Risk assessment functionality
function setupRiskAssessment() {
  updateRiskDisplay(currentRiskData);
  // Attach event listener for Calculate Risk button
  const calcBtn = document.getElementById('calculate-risk-btn');
  if (calcBtn) {
    calcBtn.addEventListener('click', calculateRisk);
  }
}

function calculateRisk() {
  showLoadingOverlay();
  // Get user input for country and crop
  const countryManual = document.getElementById('country-manual');
  const countrySelect = document.getElementById('country-select');
  let country = "";
  if (countryManual && countryManual.value.trim() !== "") {
    country = countryManual.value.trim();
  } else if (countrySelect) {
    country = countrySelect.value;
  }
  const crop = document.getElementById('crop-input').value;
  fetch('http://localhost:5000/api/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ country, crop })
  })
    .then(res => res.json())
    .then(data => {
      // Update sliders with real-time weather data
      if (data.weather) {
        setSliderValue('temperature', data.weather.temperature);
        setSliderValue('humidity', data.weather.humidity);
        setSliderValue('rainfall', data.weather.rainfall);
        setSliderValue('windspeed', data.weather.wind_speed);

        // Also update the displayed values
        updateSliderLabel('temp-value', data.weather.temperature);
        updateSliderLabel('humidity-value', data.weather.humidity);
        updateSliderLabel('rainfall-value', data.weather.rainfall);
        updateSliderLabel('wind-value', data.weather.wind_speed);
      }

      let riskScore = data.risk;
      let riskLevel, recommendation, riskClass;
      if (riskScore >= 0.7) {
        riskLevel = "High Risk";
        riskClass = "high-risk";
        recommendation = "Warning: High aphid risk predicted. Consider deploying biocontrol agents within 48 hours";
      } else if (riskScore >= 0.4) {
        riskLevel = "Medium Risk";
        riskClass = "medium-risk";
        recommendation = "Moderate aphid risk detected. Monitor crops closely and prepare treatment options";
      } else {
        riskLevel = "Low Risk";
        riskClass = "low-risk";
        recommendation = "Low aphid risk. Continue regular monitoring and maintain preventive measures";
      }
      const newRiskData = {
        currentRisk: riskScore,
        riskLevel: riskLevel,
        riskClass: riskClass,
        recommendation: recommendation
      };
      updateRiskDisplay(newRiskData);
      hideLoadingOverlay();
    })
    .catch(err => {
      hideLoadingOverlay();
      showSuccessMessage('Error fetching risk prediction');
    });
}

// Helper functions to set slider and label values
function setSliderValue(sliderId, value) {
  const slider = document.getElementById(sliderId);
  if (slider) {
    slider.value = value;
  }
}

function updateSliderLabel(labelId, value) {
  const label = document.getElementById(labelId);
  if (label) {
    label.textContent = value;
  }
}
function updateRiskDisplay(riskData) {
  const riskLevelElement = document.getElementById('risk-level');
  const riskScoreElement = document.getElementById('risk-score');
  const riskWarningElement = document.getElementById('risk-warning');
  
  if (riskLevelElement && riskScoreElement && riskWarningElement) {
    riskLevelElement.textContent = riskData.riskLevel;
    riskLevelElement.className = `risk-level ${riskData.riskClass || getRiskClass(riskData.currentRisk)}`;
    riskScoreElement.textContent = riskData.currentRisk;
    riskWarningElement.textContent = riskData.recommendation;
  }
}

function getRiskClass(riskScore) {
  if (riskScore >= 0.7) return 'high-risk';
  if (riskScore >= 0.4) return 'medium-risk';
  return 'low-risk';
}

// Chart initialization
function initializeChart() {
  const ctx = document.getElementById('riskChart');
  if (!ctx || riskChart) return;
  
  const chartData = appData.riskData.monthlyTrend;
  
  riskChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartData.map(item => item.month),
      datasets: [{
        label: 'Aphid Risk Level',
        data: chartData.map(item => item.risk),
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#4CAF50',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 1,
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            color: '#666',
            callback: function(value) {
              return (value * 100) + '%';
            }
          }
        },
        x: {
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            color: '#666'
          }
        }
      },
      elements: {
        point: {
          hoverRadius: 8
        }
      }
    }
  });
}

// Populate news section
function populateNewsSection() {
  const newsGrid = document.getElementById('news-grid');
  if (!newsGrid) return;
  
  newsGrid.innerHTML = '';
  
  appData.newsAlerts.forEach(news => {
    const newsCard = document.createElement('div');
    newsCard.className = 'news-card';
    
    newsCard.innerHTML = `
      <div class="news-header">
        <div>
          <h3 class="news-title">${news.title}</h3>
          <div class="news-date">${formatDate(news.date)}</div>
        </div>
        <span class="priority-badge">${news.priority}</span>
      </div>
      <div class="news-content">${news.content}</div>
      <a href="#" class="read-more">Read More</a>
    `;
    
    newsGrid.appendChild(newsCard);
  });
}

// Populate pesticide section
function populatePesticideSection() {
  populateRecommendations();
  populateScheduleTable();
  populateRecentApplications();
}

function populateRecommendations() {
  const recommendationsList = document.getElementById('recommendations-list');
  if (!recommendationsList) return;
  
  recommendationsList.innerHTML = '';
  
  appData.aiRecommendations.forEach(recommendation => {
    const li = document.createElement('li');
    li.textContent = recommendation;
    recommendationsList.appendChild(li);
  });
}

function populateScheduleTable() {
  const tbody = document.getElementById('schedule-tbody');
  if (!tbody) return;
  
  tbody.innerHTML = '';
  
  appData.pesticideSchedule.forEach(item => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${formatDate(item.date)}</td>
      <td>${item.targetPest}</td>
      <td>${item.treatment}</td>
      <td>${item.quantity}</td>
      <td>${item.area}</td>
      <td><span class="status-${item.status.toLowerCase()}">${item.status}</span></td>
    `;
    tbody.appendChild(row);
  });
}

function populateRecentApplications() {
  const tbody = document.getElementById('recent-tbody');
  if (!tbody) return;
  
  tbody.innerHTML = '';
  
  appData.recentApplications.forEach(item => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${formatDate(item.date)}</td>
      <td>${item.targetPest}</td>
      <td>${item.treatment}</td>
      <td>${item.quantity}</td>
      <td>${item.area}</td>
      <td><span class="status-${item.status.toLowerCase()}">${item.status}</span></td>
    `;
    tbody.appendChild(row);
  });
}

// Form handling
function setupForms() {
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', handleLogin);
  }
  
  // Google OAuth simulation
  const googleBtn = document.querySelector('.google-btn');
  if (googleBtn) {
    googleBtn.addEventListener('click', handleGoogleAuth);
  }
}

function handleLogin(e) {
  e.preventDefault();
  
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  
  if (email && password) {
    showLoadingOverlay();
    
    // Simulate login process
    setTimeout(() => {
      hideLoadingOverlay();
      closeModal();
      showSuccessMessage('Login successful! Welcome to FarmAssist.');
    }, 1500);
  }
}

function handleGoogleAuth() {
  showLoadingOverlay();
  
  // Simulate Google OAuth
  setTimeout(() => {
    hideLoadingOverlay();
    closeModal();
    showSuccessMessage('Successfully signed in with Google!');
  }, 1500);
}

// Modal functionality
function setupModalHandlers() {
  const modal = document.getElementById('login-modal');
  if (modal) {
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        closeModal();
      }
    });
  }
}

function openLoginModal() {
  const modal = document.getElementById('login-modal');
  if (modal) {
    modal.classList.remove('hidden');
  }
}

function closeModal() {
  const modal = document.getElementById('login-modal');
  if (modal) {
    modal.classList.add('hidden');
  }
}

// Loading overlay
function showLoadingOverlay() {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) {
    overlay.classList.remove('hidden');
  }
}

function hideLoadingOverlay() {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) {
    overlay.classList.add('hidden');
  }
}

// Utility functions
function formatDate(dateString) {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString(undefined, options);
}

function showSuccessMessage(message) {
  // Create and show a temporary success message
  const messageDiv = document.createElement('div');
  messageDiv.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #4CAF50;
    color: white;
    padding: 15px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    z-index: 4000;
    font-weight: 600;
  `;
  messageDiv.textContent = message;
  
  document.body.appendChild(messageDiv);
  
  // Remove after 3 seconds
  setTimeout(() => {
    messageDiv.remove();
  }, 3000);
}

// Smooth scrolling for mobile
function smoothScrollTo(element) {
  element.scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  });
}

// Add some interactive animations
function addInteractiveAnimations() {
  // Add hover effects to cards
  const cards = document.querySelectorAll('.dashboard-card, .news-card');
  cards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-5px)';
    });
    
    card.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
    });
  });
}

// Initialize animations when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(addInteractiveAnimations, 500);
});

// Handle window resize for chart responsiveness
window.addEventListener('resize', function() {
  if (riskChart) {
    riskChart.resize();
  }
});

// Keyboard navigation support
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    closeModal();
    closeAddScheduleModal();
  }
});