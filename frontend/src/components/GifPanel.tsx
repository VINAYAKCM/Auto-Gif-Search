import { Box, SimpleGrid, Image, Spinner, Center, Text } from '@chakra-ui/react';

interface GifPanelProps {
  gifs: string[];
  isLoading: boolean;
  onGifSelect: (gifUrl: string) => void;
}

export const GifPanel = ({ gifs, isLoading, onGifSelect }: GifPanelProps) => {
  return (
    <Box
      maxH="300px"
      overflowY="auto"
      borderWidth="1px"
      borderRadius="lg"
      p={2}
      bg="white"
      position="relative"
    >
      {isLoading ? (
        <Center py={8}>
          <Spinner size="lg" color="blue.500" />
        </Center>
      ) : gifs.length === 0 ? (
        <Center py={8}>
          <Text color="gray.500">No GIFs found. Try a different message!</Text>
        </Center>
      ) : (
        <SimpleGrid columns={3} spacing={2}>
          {gifs.map((gifUrl, index) => (
            <Box
              key={index}
              cursor="pointer"
              onClick={() => onGifSelect(gifUrl)}
              _hover={{ opacity: 0.8 }}
              transition="opacity 0.2s"
            >
              <Image
                src={gifUrl}
                alt={`GIF ${index + 1}`}
                borderRadius="md"
                objectFit="cover"
                w="full"
                h="100px"
                fallback={<Spinner size="sm" />}
              />
            </Box>
          ))}
        </SimpleGrid>
      )}
    </Box>
  );
}; 