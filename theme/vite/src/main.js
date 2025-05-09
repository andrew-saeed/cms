import Alpine from 'alpinejs'
import flatpickr from 'flatpickr'

import 'flatpickr/dist/flatpickr.css'
import 'flatpickr/dist/themes/dark.css'

document.addEventListener('alpine:init', () => {

    flatpickr("#id_date_of_birth", {})

    const navLinksList = document.querySelector('.links-list')

    Alpine.data('showToggler', () => ({

        open: false,

        toggle() {
            this.open = !this.open
        }
    }))

    Alpine.data('autofocusing', () => ({

        init() {
            this.$el.querySelector('input:not([type="hidden"])').focus()
        }
    }))

    Alpine.data('nav', () => ({

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

    Alpine.data('profileImage', () => ({
        init() {

            this.$refs.photoInput.addEventListener('change', (e) => {
                const file = e.target.files[0]
                if(file) {
                    const reader = new FileReader()
                    reader.onload = (e) => {
                        this.$refs.photoImg.src = e.target.result
                    }
                    reader.readAsDataURL(file)
                }
            })
        },
        openPhotoImgInput() {
            this.$refs.photoInput.click()
        }
    }))
})

Alpine.start()