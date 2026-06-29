const root = document.documentElement;
const themeToggle = document.getElementById('themeToggle');
const menuToggle = document.getElementById('menuToggle');
const navLinks = document.getElementById('navLinks');
const pageLoader = document.getElementById('pageLoader');
const typedText = document.getElementById('typedText');
const filterButtons = document.querySelectorAll('.filter-btn');
const projectCards = document.querySelectorAll('.project-card');
const readMoreButtons = document.querySelectorAll('.read-more');
const contactForm = document.getElementById('contactForm');
const formStatus = document.getElementById('formStatus');
const backTop = document.getElementById('backTop');

const phrases = ['web experiences', 'clean interfaces', 'impactful products', 'student-driven ideas'];
let phraseIndex = 0;
let charIndex = 0;
let deleting = false;

function setTheme(theme) {
  root.setAttribute('data-theme', theme);
  themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
  localStorage.setItem('portfolio-theme', theme);
}

function initTheme() {
  const storedTheme = localStorage.getItem('portfolio-theme');
  const systemTheme = window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  setTheme(storedTheme || systemTheme);
}

function typeLoop() {
  const current = phrases[phraseIndex];
  typedText.textContent = current.slice(0, charIndex);
  if (!deleting && charIndex < current.length) {
    charIndex += 1;
    setTimeout(typeLoop, 90);
  } else if (deleting && charIndex > 0) {
    charIndex -= 1;
    setTimeout(typeLoop, 45);
  } else {
    deleting = !deleting;
    if (!deleting) phraseIndex = (phraseIndex + 1) % phrases.length;
    setTimeout(typeLoop, 800);
  }
}

function initReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('show');
        if (entry.target.classList.contains('skill-item')) {
          entry.target.querySelector('.progress span')?.style.setProperty('width', entry.target.querySelector('.progress span').style.width);
        }
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });

  document.querySelectorAll('.reveal').forEach((section) => observer.observe(section));
}

function animateProgressBars() {
  document.querySelectorAll('.skill-item').forEach((item) => {
    const bar = item.querySelector('.progress span');
    const targetWidth = bar.style.width;
    bar.style.width = '0';
    setTimeout(() => { bar.style.width = targetWidth; }, 200);
  });
}

function initFilters() {
  filterButtons.forEach((button) => {
    button.addEventListener('click', () => {
      filterButtons.forEach((btn) => btn.classList.remove('active'));
      button.classList.add('active');
      const filter = button.dataset.filter;
      projectCards.forEach((card) => {
        const match = filter === 'all' || card.dataset.category === filter;
        card.style.display = match ? 'block' : 'none';
      });
    });
  });
}

function initBlog() {
  readMoreButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const target = document.getElementById(button.dataset.target);
      target.classList.toggle('show');
      button.textContent = target.classList.contains('show') ? 'Show less' : 'Read more';
    });
  });
}

function initForm() {
  contactForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(contactForm);
    const name = formData.get('name')?.toString().trim();
    const email = formData.get('email')?.toString().trim();
    const message = formData.get('message')?.toString().trim();

    if (!name || !email || !message) {
      formStatus.textContent = 'Please complete all fields.';
      return;
    }

    const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    if (!emailValid) {
      formStatus.textContent = 'Please enter a valid email address.';
      return;
    }

    formStatus.textContent = 'Sending your message...';

    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, message })
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to send message');
      }

      formStatus.textContent = 'Thanks for reaching out! Your message was received successfully.';
      contactForm.reset();
    } catch (error) {
      console.error('Contact form error:', error);
      formStatus.textContent = 'Message could not be sent right now. Please email me directly at chouguleparas498@gmail.com.';
    }
  });
}

function initBackTop() {
  window.addEventListener('scroll', () => {
    backTop.style.display = window.scrollY > 500 ? 'inline-flex' : 'none';
  });
  backTop.addEventListener('click', (event) => {
    event.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

themeToggle.addEventListener('click', () => {
  const nextTheme = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  setTheme(nextTheme);
});

menuToggle.addEventListener('click', () => {
  navLinks.classList.toggle('open');
});

document.querySelectorAll('.nav-links a').forEach((link) => {
  link.addEventListener('click', () => navLinks.classList.remove('open'));
});

window.addEventListener('load', () => {
  setTimeout(() => pageLoader.classList.add('hidden'), 600);
  initReveal();
  animateProgressBars();
  typeLoop();
});

initTheme();
initFilters();
initBlog();
initForm();
initBackTop();
