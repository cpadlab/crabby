import { BrowserRouter } from 'react-router-dom';
import { ComposeProviders } from './compose';
import { ConnectionsProvider } from '@/context/connections';

export const Providers = ComposeProviders(
    BrowserRouter,
    ConnectionsProvider,
);