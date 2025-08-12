// Elements
const display = document.getElementById('display');
const buttons = document.querySelectorAll('.btn');

// Calculator state
let currentInput = '0';
let previousInput = null;
let operator = null;
let resetDisplay = false;

// Update display helper
function updateDisplay() {
  display.textContent = currentInput;
}

// Clear all input
function clearAll() {
  currentInput = '0';
  previousInput = null;
  operator = null;
  resetDisplay = false;
  updateDisplay();
}

// Append number or decimal
function appendNumber(num) {
  if (resetDisplay) {
    currentInput = num;
    resetDisplay = false;
  } else {
    if (currentInput === '0' && num !== '.') {
      currentInput = num;
    } else if (num === '.' && currentInput.includes('.')) {
      return; // prevent multiple decimals
    } else {
      currentInput += num;
    }
  }
  updateDisplay();
}

// Choose operator
function chooseOperator(op) {
  if (operator !== null) {
    calculate();
  }
  previousInput = currentInput;
  operator = op;
  resetDisplay = true;
}

// Calculate function
function calculate() {
  if (operator === null || resetDisplay) return;

  let prev = parseFloat(previousInput);
  let current = parseFloat(currentInput);
  let result = 0;

  switch(operator) {
    case '+':
      result = prev + current;
      break;
    case '-':
      result = prev - current;
      break;
    case '*':
      result = prev * current;
      break;
    case '/':
      if (current === 0) {
        alert("Cannot divide by zero");
        clearAll();
        return;
      }
      result = prev / current;
      break;
    default:
      return;
  }

  currentInput = String(result);
  operator = null;
  previousInput = null;
  resetDisplay = true;
  updateDisplay();
}

// Event listeners for buttons
buttons.forEach(button => {
  button.addEventListener('click', () => {
    if (button.classList.contains('btn-number')) {
      appendNumber(button.textContent);
    } else if (button.classList.contains('btn-decimal')) {
      appendNumber('.');
    } else if (button.classList.contains('btn-operator')) {
      chooseOperator(button.getAttribute('data-operator'));
    } else if (button.classList.contains('btn-ac')) {
      clearAll();
    } else if (button.classList.contains('btn-equals')) {
      calculate();
    }
  });
});

// Initialize display
updateDisplay();
