import Alpinejs from 'alpinejs'

document.addEventListener('alpine:init', () => {

    const navLinksList = document.querySelector('.links-list')
    const avatarMenu = document.querySelector('.avatar-menu')

    Alpinejs.data('avatar', () => ({

        open: false,

        toggle() {
            this.open = !this.open
        }

    }))

    Alpinejs.data('nav', () => ({

        open: false,

        init() {
            navLinksList.style.maxHeight = '0px'
        },
        toggle() {
            if(navLinksList.style.maxHeight === '0px') {
                navLinksList.style.maxHeight = navLinksList.scrollHeight + 'px'
            } else {
                navLinksList.style.maxHeight = '0px'
            }
            this.open = !this.open
        }
    }))
})

Alpinejs.start()