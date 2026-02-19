import gradio as gr
import io
import contextlib
from clioraOps_cli.core.app import ClioraOpsApp
from clioraOps_cli.core.modes import Mode

class WebInterface:
    def __init__(self):
        self.app_beginner = ClioraOpsApp(Mode.BEGINNER)
        self.app_architect = ClioraOpsApp(Mode.ARCHITECT)
    
    def chat(self, message, mode, history):
        """Handle chat message."""
        app = self.app_beginner if mode == "Beginner" else self.app_architect
        
        # Capture stdout for commands
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            # Check if it's a conversation or a command
            if hasattr(app.session, 'conversation') and app.session.conversation.is_conversational_input(message):
                response = app.session.conversation.handle_conversation(message)
                if response:
                    print(response)
            else:
                app.command_router.route(message)
        
        output = f.getvalue() or "No output."
        
        history.append((message, output))
        return "", history
    
    def create_interface(self):
        """Create Gradio interface."""
        
        with gr.Blocks(title="ClioraOps") as interface:
            gr.Markdown("# 🚀 ClioraOps - DevOps Learning Companion")
            
            with gr.Row():
                mode = gr.Radio(
                    choices=["Beginner", "Architect"],
                    value="Beginner",
                    label="Mode"
                )
            
            chatbot = gr.Chatbot(label="Conversation")
            
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Ask a question or try a command...",
                    show_label=False,
                    scale=4
                )
                submit = gr.Button("Send", scale=1)
            
            # Examples
            gr.Examples(
                examples=[
                    ["try docker ps"],
                    ["design microservices"],
                    ["what is Kubernetes?"],
                    ["explain CI/CD"],
                ],
                inputs=msg
            )
            
            # Chat logic
            submit.click(
                self.chat,
                inputs=[msg, mode, chatbot],
                outputs=[msg, chatbot]
            )
            
            msg.submit(
                self.chat,
                inputs=[msg, mode, chatbot],
                outputs=[msg, chatbot]
            )
        
        return interface
    
    def launch(self, share=False):
        """Launch web interface."""
        interface = self.create_interface()
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=share  # Set True for public URL
        )

if __name__ == "__main__":
    web = WebInterface()
    web.launch(share=False)