from kivy.app import App
from kivy.clock import mainthread
from kivy.core.window import Window

from android import activity, mActivity
from jnius import autoclass

Intent = autoclass('android.content.Intent')
DocumentsContract = autoclass('android.provider.DocumentsContract')
Document = autoclass('android.provider.DocumentsContract$Document')


class ChooserDir:
    def __init__(self, callback=None, **kwargs):
        self.REQUEST_CODE = 42  # Unique request ID
        self.callback = callback

    def choose_dir(self, type_dir="music"):
        activity.bind(on_activity_result=self.intent_callback)
        App.get_running_app().bind(on_resume=self.begone_you_black_screen)
        self.set_intent()

    def set_intent(self):
        intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE)
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        mActivity.startActivityForResult(intent, self.REQUEST_CODE)

    def intent_callback(self, requestCode, resultCode, intent):
        activity.unbind(on_activity_result=self.intent_callback)
        files_list = []

        if requestCode == self.REQUEST_CODE:
            root_uri = intent.getData()
            root_id = DocumentsContract.getTreeDocumentId(root_uri)
            children = DocumentsContract.buildChildDocumentsUriUsingTree(
                root_uri, root_id)
            contentResolver = mActivity.getContentResolver()
            info = [Document.COLUMN_DISPLAY_NAME]
            c = contentResolver.query(children, info, None, None, None)

            while c.moveToNext():
                name = str(c.getString(0))
                if 'rce_plugin' not in name:  # junk from Kindle App
                    files_list.append(name)
            c.close()

            if self.callback:
                self.callback(files_list)

    # On return from the Chooser this Kivy app sometimes has a black screen,
    # but its event loop is running.
    # This workaround is scheduled in choose_content() to occur on_resume
    @mainthread
    def begone_you_black_screen(self, arg):
        App.get_running_app().unbind(on_resume=self.begone_you_black_screen)
        Window.update_viewport()
