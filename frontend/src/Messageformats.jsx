export const Textmessageform = (words) =>{
    const id = Date.now();

    return [
        { 
            id : id,
            from : 'user',
            content : 'text',
            text : words
        },
        {
            id : id+1,
            from : 'bot',
            content : 'text',
            text : 'Typing...'
        }
    ]
}

export const Audiomessageform = (audiourl) =>{
    const id = Date.now();

    return [
       {
        id: id,
        from: 'user',
        content: 'audio',
        text: audiourl
      },
      {
        id: id + 1,
        from: 'bot',
        content: 'text',
        text: 'Typing...'
      }
    ]
}

export const Imagemessageform = (imageurl, content, isaudio) =>{
    const id = Date.now();

    return [
       {
        id: id,
        from: 'user',
        content: 'image',
        image: imageurl,
        text: content,
        audio: isaudio
      },
      {
        id: id + 1,
        from: 'bot',
        content: 'text',
        text: 'Typing...'
      }
    ]
}