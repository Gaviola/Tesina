# XeLaTeX con -shell-escape (requerido por minted) y biber.
$pdf_mode = 5;
$xelatex = 'xelatex -shell-escape -synctex=1 -interaction=nonstopmode -file-line-error %O %S';

# Glosario y acrónimos: latexmk no ejecuta makeglossaries por defecto.
add_cus_dep('glo', 'gls', 0, 'run_makeglossaries');
add_cus_dep('acn', 'acr', 0, 'run_makeglossaries');

sub run_makeglossaries {
    my ($base_name, $path) = fileparse($_[0]);
    my @args = ($base_name);
    # Si el .aux todavía no tiene la información del glosario (primera pasada o .aux viejo), se omite:
    # latexmk vuelve a llamar a esta regla después de correr xelatex.
    my $aux = "$path$base_name.aux";
    if (open(my $fh, '<', $aux)) {
        local $/; my $content = <$fh>; close($fh);
        return 0 unless $content =~ /\\\@istfilename/;
    } else {
        return 0;
    }
    pushd($path);
    my $return = system('makeglossaries', @args);
    popd();
    return $return;
}

push @generated_exts, 'glo', 'gls', 'glg', 'acn', 'acr', 'alg', 'ist';
