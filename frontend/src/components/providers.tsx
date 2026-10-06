import { BrowserRouter } from 'react-router-dom';
import { ComposeProviders } from './compose';

export const Providers = ComposeProviders(
    BrowserRouter,
);