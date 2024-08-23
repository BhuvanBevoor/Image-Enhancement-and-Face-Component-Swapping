import os
import argparse
import numpy as np
from tqdm import tqdm
from PIL import Image

import torch
import torchvision.transforms.functional as tf

from src import model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--example-path', type=str, default='./image_enhancement/example', help='')
    parser.add_argument('--pretrained', type=str, default='./pretrained/enhancer.pth', help='')
    args = parser.parse_known_args()[0]

    if not os.path.exists(args.example_path):
        print('Cannot find the example path: {0}'.format(args.example_path))
        exit()
    if not os.path.exists(args.pretrained):
        print('Cannot find the pretrained model: {0}'.format(args.pretrained))
        exit()


    os.makedirs(os.path.join(args.example_path, 'enhanced'), exist_ok=True)
    with open("output.txt", "a") as output_file:
        message = "Enhancing...\n"
        output_file.write(message)
    enhancer = model.Enhancer()

    enhancer.load_state_dict(torch.load(args.pretrained, map_location=torch.device('cpu')), strict=True)
    enhancer.eval()

    with open("output.txt", "a") as output_file:
        message = "Pixelating\n"
        output_file.write(message)
    examples = os.listdir(os.path.join(args.example_path, 'original'))
    pbar = tqdm(examples, total=len(examples), unit='example')
    for i, example in enumerate(pbar):
        # load the example
        original = Image.open(os.path.join(args.example_path, 'original', example)).convert('RGB')
        original = tf.to_tensor(original)[None, ...]

        mask = original * 0 + 1

        with torch.no_grad():
            arguments = enhancer.predict_arguments(original, mask)
            enhanced = enhancer.restore_image(original, mask, arguments)[-1]

        # save the result
        enhanced = np.transpose(enhanced[0].cpu().numpy(), (1, 2, 0)) * 255
        enhanced = Image.fromarray(enhanced.astype(np.uint8))
        enhanced.save(os.path.join(args.example_path, 'enhanced', example))
        enhanced.save(os.path.join('FinalEnhanced.jpg'))
        enhanced.save(os.path.join('static', 'FinalEnhanced.jpg'))

    with open("output.txt", "a") as output_file:
        message = "Finished"
        output_file.write(message)
    print('\n')


if __name__ == '__main__':
    main()
