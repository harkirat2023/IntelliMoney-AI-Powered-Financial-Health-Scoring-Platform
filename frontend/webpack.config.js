import path from "path";
import { fileURLToPath } from "url";
import HtmlWebpackPlugin from "html-webpack-plugin";
import { CleanWebpackPlugin } from "clean-webpack-plugin";
import webpack from "webpack";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default (env, argv) => {
  const isProd = argv.mode === "production";

  return {
    mode: isProd ? "production" : "development",
    entry: "./src/main.jsx",
    output: {
      path: path.resolve(__dirname, "dist"),
      filename: "bundle.[contenthash].js",
      publicPath: "/",
      clean: true,
    },
    resolve: {
      extensions: [".js", ".jsx", ".json"],
      alias: {
        "@": path.resolve(__dirname, "src"),
      },
    },
    module: {
      rules: [
        {
          test: /\.(js|jsx)$/,
          exclude: /node_modules/,
          use: {
            loader: "babel-loader",
            options: {
              presets: ["@babel/preset-env", "@babel/preset-react"],
            },
          },
        },
        {
          test: /\.css$/,
          use: ["style-loader", "css-loader", "postcss-loader"],
        },
        {
          test: /\.(png|jpg|jpeg|gif|svg)$/,
          type: "asset/resource",
        },
      ],
    },
    plugins: [
      new CleanWebpackPlugin(),
      new HtmlWebpackPlugin({
        template: "./index.html",
        filename: "index.html",
      }),
      new webpack.DefinePlugin({
        "process.env": JSON.stringify({
          API_BASE_URL: process.env.API_BASE_URL || "http://localhost:8080/api/v1",
          VITE_WS_HOST: process.env.VITE_WS_HOST || "",
        }),
      }),
    ],
    devServer: isProd
      ? undefined
      : {
          static: {
            directory: path.join(__dirname, "public"),
          },
          port: 5173,
          hot: true,
          open: true,
          proxy: {
            "/api": {
              target: "http://localhost:8080",
              changeOrigin: true,
            },
          },
        },
  };
};