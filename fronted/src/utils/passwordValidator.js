const COMMON_PASSWORDS = [
  'password', 'password123', '12345678', 'qwerty123', 'admin123',
  'contraseña', '123456789', '11111111', 'abcd1234', 'password1'
];

// Patrones de secuencia de teclado
const KEYBOARD_SEQUENCES = [
  'qwerty', 'qwertyuiop', 'asdfgh', 'asdfghjkl', 'zxcvbn', 'zxcvbnm',
  '123456', '12345678', '123456789', '012345', '987654', '876543',
  'abcdef', 'abcdefgh', 'abc123', 'qwe123', '123qwe'
];

const hasSequence = (password) => {
  const lower = password.toLowerCase();

  // Verificar secuencias de teclado
  for (const seq of KEYBOARD_SEQUENCES) {
    if (lower.includes(seq)) {
      return true;
    }
  }

  // Verificar secuencias numéricas (3+ números consecutivos)
  for (let i = 0; i < password.length - 2; i++) {
    const a = parseInt(password[i]);
    const b = parseInt(password[i + 1]);
    const c = parseInt(password[i + 2]);

    if (!isNaN(a) && !isNaN(b) && !isNaN(c)) {
      if (b === a + 1 && c === b + 1) return true; // Ascendente: 1,2,3
      if (b === a - 1 && c === b - 1) return true; // Descendente: 3,2,1
    }
  }

  // Verificar secuencias alfabéticas (3+ letras consecutivas)
  for (let i = 0; i < lower.length - 2; i++) {
    const a = lower.charCodeAt(i);
    const b = lower.charCodeAt(i + 1);
    const c = lower.charCodeAt(i + 2);

    if (b === a + 1 && c === b + 1) return true; // abc
    if (b === a - 1 && c === b - 1) return true; // cba
  }

  return false;
};

const hasExcessiveRepetition = (password) => {
  let count = 1;
  for (let i = 1; i < password.length; i++) {
    if (password[i] === password[i - 1]) {
      count++;
      if (count > 3) return true;
    } else {
      count = 1;
    }
  }
  return false;
};

const isCommonPassword = (password) => {
  const lower = password.toLowerCase();
  return COMMON_PASSWORDS.includes(lower);
};

export const validatePassword = (password) => {
  const checks = {
    minLength: password.length >= 8,
    hasUpperCase: /[A-Z]/.test(password),
    hasLowerCase: /[a-z]/.test(password),
    hasNumber: /[0-9]/.test(password),
    hasSpecial: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    noSequences: !hasSequence(password),
    noRepetition: !hasExcessiveRepetition(password),
    notCommon: !isCommonPassword(password)
  };

  const allPassed = Object.values(checks).every(v => v === true);

  // Mensajes de error específicos
  const messages = [];
  if (!checks.minLength) messages.push('Al menos 8 caracteres');
  if (!checks.hasUpperCase) messages.push('Al menos una mayúscula');
  if (!checks.hasLowerCase) messages.push('Al menos una minúscula');
  if (!checks.hasNumber) messages.push('Al menos un número');
  if (!checks.hasSpecial) messages.push('Al menos un carácter especial (!@#$%^&*)');
  if (!checks.noSequences) messages.push('No uses secuencias (123, abc, qwerty)');
  if (!checks.noRepetition) messages.push('No repitas el mismo carácter más de 3 veces');
  if (!checks.notCommon) messages.push('Esta contraseña es muy común, elige otra');

  return {
    isValid: allPassed,
    checks,
    messages,
    strength: calculateStrength(checks)
  };
};

const calculateStrength = (checks) => {
  const weights = {
    minLength: 15,
    hasUpperCase: 15,
    hasLowerCase: 15,
    hasNumber: 15,
    hasSpecial: 20,
    noSequences: 10,
    noRepetition: 5,
    notCommon: 5
  };

  let score = 0;
  for (const [key, passed] of Object.entries(checks)) {
    if (passed) score += weights[key] || 0;
  }

  // Bonus por longitud extra
  return Math.min(100, score);
};

export const getStrengthColor = (strength) => {
  if (strength < 40) return '#ef4444'; // rojo
  if (strength < 70) return '#f59e0b'; // amarillo
  return '#10b981'; // verde
};

export const getStrengthLabel = (strength) => {
  if (strength < 40) return 'Débil';
  if (strength < 70) return 'Media';
  return 'Fuerte';
};