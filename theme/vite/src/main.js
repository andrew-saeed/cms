import Alpine from 'alpinejs'
import flatpickr from 'flatpickr'
import Editor from '@toast-ui/editor'

import 'flatpickr/dist/flatpickr.css'
import 'flatpickr/dist/themes/dark.css'
import '@toast-ui/editor/dist/toastui-editor.css'
import '@toast-ui/editor/dist/theme/toastui-editor-dark.css'

document.body.onload = () => {

    const markdownEditor = document.querySelector('#markdown-editor')

    if(markdownEditor) {
        
        const editor = new Editor({
            el: document.querySelector('#markdown-editor'),
            height: '31.25rem',
            initialEditType: 'markdown',
            previewStyle: 'tab',
            theme: 'dark',
            hideModeSwitch: true
        })
    }

    flatpickr("#id_date_of_birth", {})
}

document.addEventListener('alpine:init', () => {

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