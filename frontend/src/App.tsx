import { useState } from 'react'
import { Grid, GridItem } from '@chakra-ui/react'
import { ChatWindow } from './components/ChatWindow'
import { Message } from './types'
import axios from 'axios'

function App() {
  const [messages, setMessages] = useState<Message[]>([])

  const handleSendMessage = async (userId: 1 | 2, text: string, gifUrl?: string) => {
    // Add the message to the chat
    const newMessage: Message = {
      userId,
      text,
      gifUrl,
    }
    setMessages([...messages, newMessage])

    // If it's user 2's message, store it in the backend
    if (userId === 2) {
      try {
        await axios.post('http://localhost:5001/send_message_user2', {
          message: text,
        })
      } catch (error) {
        console.error('Error sending message to backend:', error)
      }
    }
  }

  return (
    <Grid
      templateColumns="repeat(2, 1fr)"
      gap={4}
      h="100vh"
      p={4}
      bg="gray.100"
    >
      <GridItem>
        <ChatWindow
          userId={1}
          messages={messages}
          onSendMessage={(text, gifUrl) => handleSendMessage(1, text, gifUrl)}
        />
      </GridItem>
      <GridItem>
        <ChatWindow
          userId={2}
          messages={messages}
          onSendMessage={(text, gifUrl) => handleSendMessage(2, text, gifUrl)}
        />
      </GridItem>
    </Grid>
  )
}

export default App
