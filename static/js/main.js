document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Navbar background change on scroll
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            document.querySelector('.navbar').style.background = 'rgba(0, 0, 0, 0.95)';
        } else {
            document.querySelector('.navbar').style.background = 'rgba(0, 0, 0, 0.9)';
        }
    });

    // Form submission handling
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const btn = this.querySelector('button[type="submit"]');
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

            // Submit form data to server
            fetch('/contact', {
                method: 'POST',
                body: new FormData(this)
            })
            .then(response => response.json())
            .then(data => {
                btn.innerHTML = '<i class="fas fa-check"></i> Sent!';
                this.reset();
                setTimeout(() => {
                    btn.innerHTML = 'Send Message';
                }, 2000);
            })
            .catch(error => {
                btn.innerHTML = '<i class="fas fa-times"></i> Error!';
                console.error('Error:', error);
                setTimeout(() => {
                    btn.innerHTML = 'Send Message';
                }, 2000);
            });
        });
    }

    // Intersection Observer for animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.feature-card, .pricing-card').forEach((el) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        observer.observe(el);
    });
});